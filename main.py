import os
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import schedule
import time
from google.colab import drive
from twilio.rest import Client

# Mount Google Drive
drive.mount('/content/drive')
MODEL_PATH = '/content/drive/MyDrive/urban-disaster-readiness/xgboost_model.json'
os.makedirs('/content/drive/MyDrive/urban-disaster-readiness', exist_ok=True)

# Set API keys
os.environ['AZURE_API_KEY'] = '9N5IOd5DqnASHQ2PvaqwXVey3WsrmRS1zepS2HiCeQMaRZB6JcB6JQQJ99BDACYeBjFrFSKQAAAgAZMP3S76'
os.environ['GOOGLE_API_KEY'] = 'AIzaSyDqFFnft_brDpZ9sipJuzbb_nDCsls-_SE'
# Set Twilio credentials
os.environ['TWILIO_ACCOUNT_SID'] = 'ACbd8a8b82501655e867c52338d5d001d8'
os.environ['TWILIO_AUTH_TOKEN'] = 'cdc1c9883b1e9947d21a79cd7754a1fd'
os.environ['TWILIO_PHONE_NUMBER'] = '+917979912842'

# Initialize Twilio client
client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])

# Define Mumbai zones (example wards)
mumbai_zones = {
    'A': {'lat': 19.0176, 'lon': 72.8562, 'name': 'Colaba'},
    'B': {'lat': 19.0288, 'lon': 72.8505, 'name': 'Sandhurst Road'},
    'C': {'lat': 19.0400, 'lon': 72.8430, 'name': 'Marine Lines'},
    # Add more zones as needed
}

# Function to fetch weather data from Azure Maps
def fetch_weather_data(lat, lon):
    url = f"https://atlas.microsoft.com/weather/currentConditions/json?api-version=1.0&query={lat},{lon}&subscription-key={os.environ['AZURE_API_KEY']}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            'temperature': data['results'][0]['temperature']['value'],
            'precipitation': data['results'][0].get('precipitationSummary', {}).get('pastHour', {}).get('value', 0),
            'wind_speed': data['results'][0]['wind']['speed']['value']
        }
    return None

# Function to fetch traffic data from Google Maps
def fetch_traffic_data(lat, lon):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={lat},{lon}&destinations={lat},{lon}&departure_time=now&key={os.environ['GOOGLE_API_KEY']}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {'traffic_duration': data['rows'][0]['elements'][0]['duration_in_traffic']['value'] / 60}
    return None

# Data collection
def collect_data():
    data = []
    for zone_id, zone in mumbai_zones.items():
        weather = fetch_weather_data(zone['lat'], zone['lon'])
        traffic = fetch_traffic_data(zone['lat'], zone['lon'])
        if weather and traffic:
            record = {
                'zone_id': zone_id,
                'lat': zone['lat'],
                'lon': zone['lon'],
                'temperature': weather['temperature'],
                'precipitation': weather['precipitation'],
                'wind_speed': weather['wind_speed'],
                'traffic_duration': traffic['traffic_duration'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            data.append(record)
    return pd.DataFrame(data)

# Preprocess data
def preprocess_data(df):
    # Add synthetic risk labels for training (replace with real labels if available)
    df['flood_risk'] = np.where((df['precipitation'] > 10) & (df['traffic_duration'] > 30), 1, 0)
    return df

# Train XGBoost model
def train_model(df):
    X = df[['temperature', 'precipitation', 'wind_speed', 'traffic_duration']]
    y = df['flood_risk']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate accuracy
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    
    # Save the model to Google Drive
    model.save_model(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    
    return model

# Generate PDF report
def generate_pdf_report(df, risk_scores, filename='/content/drive/MyDrive/urban-disaster-readiness/report.pdf'):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, "Urban Disaster Readiness Report")
    c.drawString(100, 730, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    y = 700
    for _, row in df.iterrows():
        zone_name = mumbai_zones[row['zone_id']]['name']
        text = f"Zone: {zone_name}, Risk Score: {risk_scores[row['zone_id']]:.2f}"
        text += f", Temp: {row['temperature']}°C, Precip: {row['precipitation']}mm"
        c.drawString(100, y, text)
        y -= 20
    
    c.save()
    print(f"PDF report saved as {filename}")

# Send SMS alerts
def send_sms_alerts():
    print("Checking for high-risk zones...")
    df = pd.read_csv('/content/drive/MyDrive/urban-disaster-readiness/data.csv')
    sms_sent = False
    for _, row in df.iterrows():
        print(f"Processing zone {row['zone_id']}: Precipitation = {row['precipitation']}")
        if row['precipitation'] > 10:  # Example threshold
            zone_name = mumbai_zones[row['zone_id']]['name']
            message = f"High Risk Alert in {zone_name}! Precipitation: {row['precipitation']}mm. Take precautions."
            print(f"Sending SMS for {zone_name}...")
            try:
                client.messages.create(
                    body=message,
                    from_=os.environ['TWILIO_PHONE_NUMBER'],
                    to='+917979912842'  # Replace with recipient number
                )
                print(f"SMS sent for {zone_name}")
                sms_sent = True
            except Exception as e:
                print(f"Error sending SMS for {zone_name}: {str(e)}")
    if not sms_sent:
        print("No zones met the threshold for sending SMS (precipitation > 10).")

# Backend update function
def update_backend():
    df = collect_data()
    df = preprocess_data(df)
    model = train_model(df)
    
    # Calculate risk scores
    X = df[['temperature', 'precipitation', 'wind_speed', 'traffic_duration']]
    risk_scores = model.predict_proba(X)[:, 1]
    risk_scores_dict = {df['zone_id'].iloc[i]: score for i, score in enumerate(risk_scores)}
    
    # Generate PDF report
    generate_pdf_report(df, risk_scores_dict)
    
    # Save data for heatmap and predictive analysis
    df.to_csv('/content/drive/MyDrive/urban-disaster-readiness/data.csv', index=False)
    
    # Send SMS alerts
    send_sms_alerts()
    
    print("Backend updated")

# Schedule backend updates (every hour)
schedule.every(1).hours.do(update_backend)

# Run scheduler in Colab
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)
        if __name__ == "__main__":
    update_backend()  # Initial run
    # Uncomment the following line to run the scheduler in Colab
    # run_scheduler()