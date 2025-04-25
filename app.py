from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route('/')
def index():
    return 'Urban Disaster Readiness API'

@app.route('/report')
def serve_report():
    return send_file('/content/drive/MyDrive/urban-disaster-readiness/report.pdf')

@app.route('/predictive_report')
def serve_predictive_report():
    return send_file('/content/drive/MyDrive/urban-disaster-readiness/predictive_report.pdf')

@app.route('/heatmap')
def serve_heatmap():
    return send_file('/content/drive/MyDrive/urban-disaster-readiness/heatmap.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)