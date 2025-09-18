import joblib
import pandas as pd
import requests
import json

# Load the trained model (make sure to upload the model file to the Lambda deployment package)
model = joblib.load('C:/Users/Lenovo/FlightAI/flight_cancellation_model.pkl')

# OpenWeatherMap API integration 
API_KEY = '2495e8ff5c7ba6e4eda282a59017524c'  
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def fetch_weather_data(city_name):
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'  # Temperature in Celsius
    }
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    if response.status_code == 200:
        # Mapping API response to the model's expected features
        return {
            'Feature_HourlyWindSpeed_x': data['wind']['speed'],  # Wind speed (m/s)
            'Feature_HourlyVisibility_x': data['visibility'] / 1000,  # Visibility (km)
            'Feature_HourlyPrecipitation_x': data.get('rain', {}).get('1h', 0),  # Precipitation (mm)
            'Feature_HourlyDryBulbTemperature_x': data['main']['temp'],  # Temperature (Celsius)
            'Feature_HourlyWindSpeed_y': data['wind']['speed'],  # Wind speed (m/s) for 'y' column
            'Feature_HourlyVisibility_y': data['visibility'] / 1000,  # Visibility (km) for 'y' column
            'Feature_HourlyPrecipitation_y': data.get('rain', {}).get('1h', 0),  # Precipitation (mm) for 'y' column
            'Feature_HourlyDryBulbTemperature_y': data['main']['temp'],  # Temperature (Celsius) for 'y' column
            'Feature_HourlyStationPressure_x': 1013,  # Default value for pressure, adjust as necessary
            'Feature_HourlyStationPressure_y': 1013  # Default value for pressure, adjust as necessary
        }
    else:
        return None

def lambda_handler(event, context):
    # Get input data from the event (API Gateway or other event sources)
    try:
        body = json.loads(event['body'])  # Parse the incoming JSON data
        city_name = body['city_name']
        model_input = body['model_input']
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid input data'})
        }

    # Fetch weather data for the origin city
    weather_data = fetch_weather_data(city_name)
    
    if not weather_data:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to fetch weather data'})
        }

    # Update the model input with weather data
    model_input.update(weather_data)

    # Convert input to DataFrame
    model_input_df = pd.DataFrame([model_input])

    # Apply one-hot encoding (if necessary)
    categorical_columns = ['carrier_code', 'origin_airport', 'destination_airport']
    model_input_df = pd.get_dummies(model_input_df, columns=categorical_columns)

    # Ensure model input has the same columns as the trained model
    model_input_df = model_input_df.reindex(columns=model.feature_names_in_, fill_value=0)

    # Make the prediction
    prediction = model.predict(model_input_df)
    confidence_score = model.predict_proba(model_input_df)[0][1]  # Probability of cancellation

    # Return the prediction and confidence score as a JSON response
    return {
        'statusCode': 200,
        'body': json.dumps({
            'prediction': int(prediction[0]),  # 0 = Not Cancelled, 1 = Cancelled
            'confidence_score': round(confidence_score, 2)
        })
    }
