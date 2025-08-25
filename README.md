# Weather API Dashboard v2

Python-based automation tool that retrieves real-time weather data from the OpenWeatherMap API for selected U.S. cities. Users can track weather trends, analyze local data, and create visual dashboards to support decision-making and reporting.

What's New in v2
- Automated Pulls: Enables unattended scheduling, reducing manual effort and ensuring up-to-date data.

- Local Storage: Supports easy access to historical weather, aiding in trend analysis and audits.

- Modular Structure: Facilitates adding new features for future expansion and customization.

- Testable Scripts: Simplifies testing and quick troubleshooting without affecting live data.

- City Configurations: Allows rapid adjustment for tracking weather in different locations.

Features include API integration with requests, environment key management, local JSON logs by city and time, organized data directories, and a testable runner script.

## How to Run
1. Clone the repo and install dependencies:
   ```bash
   git clone https://github.com/buildwithmanny/weather-api-dashboard-v2.git
   cd weather-api-dashboard-v2
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
