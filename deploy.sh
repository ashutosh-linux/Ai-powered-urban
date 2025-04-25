#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Set up Ngrok
ngrok authtoken $NGROK_AUTH_TOKEN

# Run Flask app
python app.py &

# Start Ngrok
ngrok http 5000