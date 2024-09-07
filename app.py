import pickle
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta

# Load the model from the pickle file
model_filename = './models/pipe.pkl'
try:
    with open(model_filename, 'rb') as file:
        model = pickle.load(file)
except Exception as e:
    print(f"Error loading the model: {e}")
    model = None

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Update with your MongoDB connection URI if different
db = client['hospitalDb']  # Your database name
hospitals_collection = db['hospitals']  # Your collection name

# Define an endpoint for prediction based on hospital name
@app.route('/api/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model is not loaded correctly'}), 500

    try:
        data = request.json
        hospital_name = data.get('hospital_name')

        if not hospital_name:
            return jsonify({'error': 'Invalid input, please provide a hospital_name'}), 400

        # Fetch hospital data from MongoDB
        hospital = hospitals_collection.find_one({'hospital_name': hospital_name})

        if not hospital:
            return jsonify({'error': 'Hospital not found'}), 404

        # Iterate over each medicine in the hospital
        predictions = []
        for medicine in hospital['medicines']:
            amount = medicine['quantity']
            consumption_average = medicine['consumption_rate']

            # Make prediction using the amount and consumption_average for each medicine
            prediction = model.predict([[amount, consumption_average]])
            predicted_days = int(prediction[0])  # Ensure prediction is an integer

            # Calculate expiry date
            today = datetime.today()
            expiry_date = today + timedelta(days=predicted_days)

            # Check if the medicine is predicted to expire soon
            is_expired = expiry_date <= today

            # Append the prediction data to the list
            predictions.append({
                'name': medicine['name'],
                'quantity': amount,
                'consumption_rate': consumption_average,
                'predicted_days': predicted_days,
                'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                'is_expired': is_expired
            })

        # Return the prediction results along with the hospital name
        return jsonify({
            'hospital_name': hospital_name,
            'predictions': predictions
        })

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
