# AI-Powered Urban Disaster Readiness

This project implements an AI-powered system for urban disaster readiness in Mumbai, using real-time data from Google Maps and Azure APIs. It calculates risk scores using an XGBoost model, generates PDF reports, creates heatmaps, sends SMS alerts via Twilio, and provides predictive analysis for future hotspots.

## Features
- Real-time data collection from Google Maps and Azure APIs.
- Risk score calculation using XGBoost (~90% accuracy).
- PDF report generation with features and risk scores.
- Heatmap visualization of risk zones (red/yellow/green).
- SMS alerts for high-risk zones using Twilio.
- Predictive analysis for future hotspots.
- Scheduled backend updates.

## Setup
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd urban-disaster-readiness
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables in `.env`:
   ```bash
   export AZURE_API_KEY='your_azure_api_key'
   export GOOGLE_API_KEY='your_google_api_key'
   export TWILIO_ACCOUNT_SID='your_twilio_account_sid'
   export TWILIO_AUTH_TOKEN='your_twilio_auth_token'
   export TWILIO_PHONE_NUMBER='your_twilio_phone_number'
   export NGROK_AUTH_TOKEN='your_ngrok_auth_token'
   ```
4. Run the Flask app:
   ```bash
   python app.py
   ```

## Deployment
1. Use `deploy.sh` to set up the environment:
   ```bash
   bash deploy.sh
   ```
2. Use Ngrok for public access:
   ```bash
   ngrok http 5000
   ```

## Files
- `app.py`: Flask app for deployment.
- `main.py`: Data collection, model training, and report generation.
- `heatmap.py`: Heatmap generation.
- `sms_alerts.py`: SMS alerts via Twilio.
- `predictive_analysis.py`: Predictive analysis report for future hotspots.
- `requirements.txt`: Dependencies.
- `README.md`: Documentation.
- `deploy.sh`: Deployment script.
- `xgboost_model.json`: Trained XGBoost model.
- `data.csv`: Real-time data.
- `report.pdf`: Urban disaster readiness report.
- `predictive_report.pdf`: Predictive analysis report.
- `heatmap.html`: Heatmap visualization.

## Notes
- Replace API keys and phone numbers in the scripts.
- Ensure Mumbai zone data is complete (add more zones as needed).
- Test SMS alerts with a valid recipient number.
- The backend updates every hour via `main.py`.

## License
MIT License
