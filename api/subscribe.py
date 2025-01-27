from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name')
        
        print(f"Processing subscription for: {email}")  # Debug logging

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
            'fields': {
                'name': name
            }
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

if __name__ == '__main__':
    app.run()