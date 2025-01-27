from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Newsletter Subscription</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
            }
            input {
                width: 100%;
                padding: 8px;
                margin-bottom: 10px;
            }
            button {
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                border: none;
                cursor: pointer;
            }
            .message {
                padding: 10px;
                margin-top: 10px;
                border-radius: 4px;
            }
            .success {
                background-color: #d4edda;
                color: #155724;
            }
            .error {
                background-color: #f8d7da;
                color: #721c24;
            }
        </style>
    </head>
    <body>
        <h1>Subscribe to Mav's letter (* .ˬ.)"</h1>
        <form id="subscribeForm">
            <div class="form-group">
                <label for="name">Name</label>
                <input type="text" id="name" name="name" required>
            </div>
            <div class="form-group">
                <label for="email">Email (to receive the letters)</label>
                <input type="email" id="email" name="email" required>
            </div>
            <button type="submit">Gooo!</button>
        </form>
        <div id="message"></div>

        <script>
            document.getElementById('subscribeForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const messageDiv = document.getElementById('message');
                
                try {
                    const response = await fetch('/api/subscribe', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: document.getElementById('name').value,
                            email: document.getElementById('email').value
                        })
                    });

                    const data = await response.json();
                    
                    if (response.ok) {
                        messageDiv.className = 'message success';
                        messageDiv.textContent = 'Successfully subscribed!';
                        document.getElementById('subscribeForm').reset();
                    } else {
                        messageDiv.className = 'message error';
                        messageDiv.textContent = data.message || 'Subscription failed';
                    }
                } catch (error) {
                    messageDiv.className = 'message error';
                    messageDiv.textContent = 'An error occurred. Please try again.';
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name')

        if not email or not name:
            return jsonify({'message': 'Email and name are required'}), 400

        # Get API key and group ID from environment variables
        api_key = os.environ.get('MAILERLITE_API_KEY')
        group_id = os.environ.get('MAILERLITE_GROUP_ID')

        # First, create the subscriber
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        # Create subscriber
        create_url = 'https://connect.mailerlite.com/api/subscribers'
        payload = {
            'email': email,
            'name': name
        }

        response = requests.post(create_url, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            subscriber_data = response.json().get('data', {})
            subscriber_id = subscriber_data.get('id')

            # If we have both subscriber_id and group_id, add to group
            if subscriber_id and group_id:
                group_url = f'https://connect.mailerlite.com/api/subscribers/{subscriber_id}/groups/{group_id}'
                group_response = requests.post(group_url, headers=headers)
                
                if group_response.status_code in [200, 201]:
                    return jsonify({'message': 'Successfully subscribed and added to group!'}), 200
                else:
                    print(f"Group assignment failed: {group_response.text}")
                    # Still return success since the subscription worked
                    return jsonify({'message': 'Successfully subscribed!'}), 200
            
            return jsonify({'message': 'Successfully subscribed!'}), 200
        else:
            error_message = 'Subscription failed'
            try:
                error_data = response.json()
                if isinstance(error_data, dict) and 'error' in error_data:
                    error_message = error_data['error']
            except:
                pass
            return jsonify({'message': error_message}), 400

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': 'Error processing subscription'}), 500