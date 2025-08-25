from dotenv import load_dotenv
import os, json, csv, logging, argparse
from pathlib import Path
from datetime import datetime, timezone
import requests
import pandas as pd
import matplotlib.pyplot as plt

# ======= PROJECT PATH & ENV =======
PROJECT_DIR = Path(__file__).resolve().parent  # <— always the folder main.py lives in
load_dotenv(PROJECT_DIR / ".env")              # <— explicitly load .env from the project
API_KEY = os.getenv("OPENWEATHER_API_KEY")
print(f"🔍 DEBUG — API KEY Loaded: {bool(API_KEY)}")

# ======= SETTINGS =======
CITIES = ["Los Angeles", "San Francisco", "Seattle", "New York", "Miami", "San Diego"]
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
UNITS = "imperial"  # or "metric"/"standard"

# ======= LOGGING =======
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

# ======= HELPERS =======
def utc_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def ensure_dirs():
    (PROJECT_DIR / "data").mkdir(parents=True, exist_ok=True)
    (PROJECT_DIR / "visuals").mkdir(parents=True, exist_ok=True)

# ======= FETCH =======
def get_weather(city_name: str):
    params = {"q": city_name, "appid": API_KEY, "units": UNITS}
    r = requests.get(OPENWEATHER_URL, params=params, timeout=20)
    r.raise_for_status()
    d = r.json()

    coord = d.get("coord", {})
    main = d.get("main", {})
    wind = d.get("wind", {})
    wlist = d.get("weather", [])
    desc = wlist[0]["description"] if wlist else None

    return {
        "city": d.get("name") or city_name,
        "lat": coord.get("lat"),
        "lon": coord.get("lon"),
        "temperature_F": main.get("temp"),
        "feels_like_F": main.get("feels_like"),
        "temp_min_F": main.get("temp_min"),
        "temp_max_F": main.get("temp_max"),
        "humidity_percent": main.get("humidity"),
        "pressure_hPa": main.get("pressure"),
        "wind_mph": wind.get("speed"),
        "weather_description": desc,
        "timestamp_utc": utc_iso(),
    }

# ======= IO =======
def save_json_overwrite(records):
    """Overwrite a single JSON snapshot each run (keeps project light)."""
    out = PROJECT_DIR / "data" / "weather_data_latest.json"
    payload = {
        "metadata": {
            "generated_utc": utc_iso(),
            "source": OPENWEATHER_URL,
            "records": len(records)
        },
        "data": records
    }
    out.write_text(json.dumps(payload, indent=2))
    logging.info(f" JSON updated (overwritten): {out}")

def append_csv(records, csv_path: Path):
    """Append new rows to the one CSV (growing history)."""
    exists = csv_path.exists()
    with csv_path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        if not exists:
            writer.writeheader()
        writer.writerows(records)
    logging.info(f"📈 Appended {len(records)} rows → {csv_path}")

def load_dataframe(csv_path: Path):
    if not csv_path.exists():
        logging.warning(" No CSV yet.")
        return None
    df = pd.read_csv(csv_path)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
    df = df.sort_values("timestamp_utc")
    return df

# ======= PLOT (single PNG overwrite) =======
def plot_from_csv(csv_path: Path, visuals_dir: Path, last=400, resample=None, city=None):
    df = load_dataframe(csv_path)
    if df is None or df.empty:
        logging.warning("No data to plot.")
        return

    # Cutoff at 2025-08-17
    cutoff = pd.Timestamp("2025-08-17T00:00:00Z")
    df = df[df["timestamp_utc"] <= cutoff]

    if city:
        df = df[df["city"] == city]
        if df.empty:
            logging.warning(f"No data for city={city}")
            return

    df = df.set_index("timestamp_utc")

    if resample:
        df = (df.groupby("city")
                .resample(resample).mean(numeric_only=True)
                .reset_index().set_index("timestamp_utc"))

    piv = df.pivot_table(index="timestamp_utc", columns="city", values="temperature_F")

    # Always keep the full dataset to preserve 145 lines
    if last:
        piv = piv.tail(last)

    visuals_dir.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(12, 6))

    # Plot lines
    piv.plot(ax=plt.gca(), marker="o", linewidth=1.8, markersize=4)

    plt.title("Temperature Trend (Up to Aug 17, 2025)")
    plt.xlabel("Timestamp (UTC)")
    plt.ylabel("Temperature (°F)")
    plt.tight_layout()

    latest = visuals_dir / "temperature_trend_latest.png"
    plt.savefig(latest, dpi=150)
    plt.close()
    logging.info(f"🖼️ Hybrid line + dot plot saved: {latest}")

# ======= CLI (optional filters) =======
def parse_args():
    p = argparse.ArgumentParser(description="Fetch weather, append CSV, overwrite JSON & plot.")
    p.add_argument("--city", type=str, default=None, help="Plot only this city")
    p.add_argument("--last", type=int, default=400, help="Plot last N points")
    p.add_argument("--resample", type=str, default=None, help='e.g. "15min", "1H" to time-bucket')
    return p.parse_args()

# ======= MAIN =======
def main():
    if not API_KEY:
        raise SystemExit("Missing OPENWEATHER_API_KEY in .env")

    args = parse_args()
    ensure_dirs()

    # fetch
    records = []
    for c in CITIES:
        try:
            rec = get_weather(c)
            records.append(rec)
            logging.info(f"✓ {rec['city']}: {rec['temperature_F']}°F, {rec['weather_description']}")
        except requests.HTTPError as e:
            logging.warning(f"HTTP {e.response.status_code} for {c}: {e.response.text[:120]}")
        except requests.RequestException as e:
            logging.warning(f"Network error for {c}: {e}")

    if not records:
        logging.error("No records fetched; skipping save and plot.")
        return

    # write outputs
    save_json_overwrite(records)                                 # overwrite single JSON
    csv_path = PROJECT_DIR / "data" / "weather_history.csv"
    append_csv(records, csv_path)                                # append rows to single CSV
    plot_from_csv(csv_path, PROJECT_DIR / "visuals",             # overwrite single PNG
                  last=args.last, resample=args.resample, city=args.city)

if __name__ == "__main__":
    main()
