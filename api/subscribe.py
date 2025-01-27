# api/subscribe.py
from flask import Flask, request, jsonify, render_template
import mailerlite as MailerLite
import os

app = Flask(__name__)

# Initialize MailerLite client
client = MailerLite.Client({
    'api_key': os.environ.get('MAILERLITE_API_KEY')
})

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

        # Create subscriber in MailerLite
        response = client.subscribers.create(
            email,
            fields={'name': name}
        )

        return jsonify({'message': 'Successfully subscribed'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': 'Error processing subscription'}), 500

if __name__ == '__main__':
    app.run()