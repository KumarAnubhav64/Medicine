import pickle
from flask import Flask, request, jsonify



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

# Define an endpoint for prediction
@app.route('/api/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model is not loaded correctly'}), 500

    try:
        data = request.json
        amount = data.get('amount')
        consumption_average = data.get('consumption_average')

        # Validate inputs
        if amount is None or consumption_average is None:
            return jsonify({'error': 'Invalid input, please provide both amount and consumption_average'}), 400

        # Make prediction
        prediction = model.predict([[amount, consumption_average]])

        # Return the prediction as a JSON response
        return jsonify({'predicted_days': prediction[0]})

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
