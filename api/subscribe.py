# api/subscribe.py
from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name')

        if not email or not name:
            return jsonify({'message': 'Email and name are required'}), 400

        # MailerLite API endpoint
        api_url = 'https://api.mailerlite.com/api/v2/subscribers'
        headers = {
            'Content-Type': 'application/json',
            'X-MailerLite-ApiKey': os.environ.get('MAILERLITE_API_KEY')
        }
        payload = {
            'email': email,
            'name': name
        }

        # Make request to MailerLite API
        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return jsonify({'message': 'Successfully subscribed'}), 200
        else:
            return jsonify({'message': 'Error from MailerLite API'}), response.status_code

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': 'Error processing subscription'}), 500

if __name__ == '__main__':
    app.run()