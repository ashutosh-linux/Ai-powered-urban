import os
from twilio.rest import Client
import pandas as pd
from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# Set Twilio credentials
os.environ['TWILIO_ACCOUNT_SID'] = 'ACbd8a8b82501655e867c52338d5d001d8'
os.environ['TWILIO_AUTH_TOKEN'] = 'cdc1c9883b1e9947d21a79cd7754a1fd'
os.environ['TWILIO_PHONE_NUMBER'] = '+917979912842'

# Initialize Twilio client
print("Initializing Twilio client...")
try:
    client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
    print("Twilio client initialized successfully")
except Exception as e:
    print(f"Error initializing Twilio client: {str(e)}")
    exit(1)

# Load data
print("Loading data.csv...")
try:
    df = pd.read_csv('/content/drive/MyDrive/urban-disaster-readiness/data.csv')
    print("Data loaded successfully")
    print("Data preview:")
    print(df.head())
except Exception as e:
    print(f"Error loading data: {str(e)}")
    exit(1)

# Mumbai zones
mumbai_zones = {
    'A': {'lat': 19.0176, 'lon': 72.8562, 'name': 'Colaba'},
    'B': {'lat': 19.0288, 'lon': 72.8505, 'name': 'Sandhurst Road'},
    'C': {'lat': 19.0400, 'lon': 72.8430, 'name': 'Marine Lines'},
}

# Send SMS alerts
def send_sms_alerts():
    print("Checking for high-risk zones...")
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

if __name__ == "__main__":
    send_sms_alerts()# Paste the entire updated sms_alerts.py content here
