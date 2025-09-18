import json
import requests
from datetime import datetime
import logging

# Setup logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

def lambda_handler(event, context):
    try:
        path = event.get("rawPath", "")
        params = event.get("queryStringParameters", {}) or {}

        logger.debug("DEBUG: path=%s, params=%s", path, params)

        if "dashboard-flights" in path:
            return get_dashboard_data(params)

        return get_single_flight(params)

    except Exception as e:
        logger.exception("Unhandled exception in lambda_handler")
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Internal error", "error": str(e)})
        }

def get_single_flight(params):
    flight_number = params.get("flightNumber", "DL345")
    flight_date = params.get("date", "2025-07-11")
    url = f"https://aerodatabox.p.rapidapi.com/flights/number/{flight_number}/{flight_date}"

    headers = {
        "x-rapidapi-host": "aerodatabox.p.rapidapi.com",
        "x-rapidapi-key": "YOUR_API_KEY"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            logger.warning("API quota exceeded. Returning mock flight data.")
            return {
                "statusCode": 200,
                "headers": cors_headers(),
                "body": json.dumps({
                    "flight_number": "DL345",
                    "status": "EnRoute",
                    "departure": "Atlanta Hartsfield",
                    "arrival": "JFK International",
                    "departure_time": "2025-07-11T14:00",
                    "arrival_time": "2025-07-11T16:30",
                    "aircraft": "Airbus A321",
                    "airline": "Delta Air Lines"
                })
            }
        else:
            raise e
    except Exception as e:
        logger.exception("RequestException in get_single_flight")
        return {
            "statusCode": 502,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Error fetching flight data", "error": str(e)})
        }

    if isinstance(data, list):
        data = {"departures": data}

    if not data.get("departures"):
        return {
            "statusCode": 404,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Flight not found"})
        }

    flight = data["departures"][0]

    result = {
        "flight_number": flight.get("number", "N/A"),
        "status": flight.get("status", "N/A"),
        "departure": flight.get("departure", {}).get("airport", {}).get("name", "N/A"),
        "arrival": flight.get("arrival", {}).get("airport", {}).get("name", "N/A"),
        "departure_time": flight.get("departure", {}).get("scheduledTime", {}).get("local", "N/A"),
        "arrival_time": flight.get("arrival", {}).get("scheduledTime", {}).get("local", "N/A"),
        "aircraft": flight.get("aircraft", {}).get("model", "N/A"),
        "airline": flight.get("airline", {}).get("name", "N/A")
    }

    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps(result)
    }

def get_dashboard_data(params):
    logger.debug("DEBUG: Raw params in dashboard: %s", params)

    if not isinstance(params, dict):
        logger.error("Invalid type for params. Expected dict, got: %s", type(params).__name__)
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Invalid query parameters format", "error": str(params)})
        }

    today = datetime.utcnow().strftime('%Y-%m-%d')
    airport = params.get("airport", "ATL")
    url = f"https://aerodatabox.p.rapidapi.com/flights/airports/icao/{airport}/{today}T00:00/{today}T23:59"

    headers = {
        "x-rapidapi-host": "aerodatabox.p.rapidapi.com",
        "x-rapidapi-key": "YOUR_API_KEY"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            logger.warning("API quota exceeded. Returning mock dashboard data.")
            return {
                "statusCode": 200,
                "headers": cors_headers(),
                "body": json.dumps({
                    "summary": {"on_time": 18, "delayed": 7, "cancelled": 5},
                    "flights": [
                        {"flight_number": "DL401", "airline": "Delta", "status": "On Time", "departure_time": "10:00", "arrival_time": "12:00"},
                        {"flight_number": "DL402", "airline": "Delta", "status": "Delayed", "departure_time": "12:30", "arrival_time": "14:50"},
                        {"flight_number": "DL403", "airline": "Delta", "status": "Cancelled", "departure_time": "15:00", "arrival_time": "17:00"},
                    ]
                })
            }
        else:
            raise e
    except Exception as e:
        logger.exception("Exception in get_dashboard_data")
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Dashboard fetch failed", "error": str(e)})
        }

    flights = data.get("departures", []) + data.get("arrivals", [])
    summary = {"on_time": 0, "delayed": 0, "cancelled": 0}
    flight_rows = []

    for f in flights[:30]:
        status = f.get("status", "").lower()
        if "cancel" in status:
            summary["cancelled"] += 1
        elif "delay" in status:
            summary["delayed"] += 1
        else:
            summary["on_time"] += 1

        flight_rows.append({
            "flight_number": f.get("number", "N/A"),
            "airline": f.get("airline", {}).get("name", "N/A"),
            "status": f.get("status", "N/A"),
            "departure_time": f.get("departure", {}).get("scheduledTime", {}).get("local", "N/A"),
            "arrival_time": f.get("arrival", {}).get("scheduledTime", {}).get("local", "N/A")
        })

    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps({"summary": summary, "flights": flight_rows})
    }

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*"
    }
