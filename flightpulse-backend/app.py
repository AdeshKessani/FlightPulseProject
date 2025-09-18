import json
import requests
from datetime import datetime, timedelta
import logging

# Setup logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Your RapidAPI key
RAPIDAPI_KEY = "8c921033d1mshf4e328256bfbd9fp12f1e3jsnb6c28948835a"

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Content-Type": "application/json"
    }

def lambda_handler(event, context):
    # support both HTTP API v2 and REST API events
    path   = event.get("rawPath") or event.get("path", "")
    params = event.get("queryStringParameters") or {}
    logger.debug("DEBUG: path=%s, params=%s", path, params)

    if path.endswith("/dashboard-flights"):
        return get_dashboard_data(params)
    elif path.endswith("/check-flight"):
        return get_single_flight(params)
    else:
        return {
            "statusCode": 404,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Not Found"})
        }

def get_single_flight(params):
    """
    /check-flight?flightNumber=XXX&date=YYYY-MM-DD
    """
    flight_number = params.get("flightNumber")
    flight_date   = params.get("date")

    if not flight_number or not flight_date:
        return {
            "statusCode": 400,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Missing flightNumber or date"})
        }

    url = f"https://aerodatabox.p.rapidapi.com/flights/number/{flight_number}/{flight_date}"
    headers = {
        "x-rapidapi-host": "aerodatabox.p.rapidapi.com",
        "x-rapidapi-key":  RAPIDAPI_KEY
    }

    resp = requests.get(url, headers=headers, timeout=10)
    logger.debug("Flight GET %s → %s", resp.url, resp.status_code)
    if resp.status_code != 200:
        return {
            "statusCode": resp.status_code,
            "headers": cors_headers(),
            "body": json.dumps({
                "error":       "RapidAPI flight call failed",
                "status_code": resp.status_code,
                "detail":      resp.text
            })
        }

    data = resp.json()
    if isinstance(data, list):
        data = {"departures": data}

    departures = data.get("departures", [])
    if not departures:
        return {
            "statusCode": 404,
            "headers": cors_headers(),
            "body": json.dumps({"message": "Flight not found"})
        }

    f = departures[0]
    result = {
        "flight_number":  f.get("number"),
        "status":         f.get("status"),
        "departure":      f.get("departure", {}).get("airport", {}).get("name"),
        "arrival":        f.get("arrival",   {}).get("airport", {}).get("name"),
        "departure_time": f.get("departure", {}).get("scheduledTime", {}).get("local"),
        "arrival_time":   f.get("arrival",   {}).get("scheduledTime", {}).get("local"),
        "aircraft":       f.get("aircraft", {}).get("model"),
        "airline":        f.get("airline",  {}).get("name")
    }

    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps(result)
    }

def get_dashboard_data(params):
    """
    /dashboard-flights?airport=XXX

    Uses a sliding 12‑hour window (now‑12h to now) to satisfy Aerodatabox limits.
    """
    # default to ATL if none provided
    airport = params.get("airport", "ATL")

    # compute 12h window
    end   = datetime.utcnow()
    start = end - timedelta(hours=12)
    start_str = start.strftime("%Y-%m-%dT%H:%M")
    end_str   = end.strftime(  "%Y-%m-%dT%H:%M")

    url = (
        f"https://aerodatabox.p.rapidapi.com/"
        f"flights/airports/icao/{airport}/"
        f"{start_str}/{end_str}"
    )
    headers = {
        "x-rapidapi-host": "aerodatabox.p.rapidapi.com",
        "x-rapidapi-key":  RAPIDAPI_KEY
    }

    resp = requests.get(url, headers=headers, timeout=10)
    logger.debug("Dashboard GET %s → %s", resp.url, resp.status_code)
    if resp.status_code != 200:
        return {
            "statusCode": resp.status_code,
            "headers": cors_headers(),
            "body": json.dumps({
                "error":       "RapidAPI dashboard call failed",
                "status_code": resp.status_code,
                "detail":      resp.text
            })
        }

    data    = resp.json()
    flights = data.get("departures", []) + data.get("arrivals", [])
    summary = {"on_time": 0, "delayed": 0, "cancelled": 0}

    for f in flights:
        st = (f.get("status") or "").lower()
        if "cancel" in st:
            summary["cancelled"] += 1
        elif "delay" in st:
            summary["delayed"]   += 1
        else:
            summary["on_time"]   += 1

    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps({"summary": summary})
    }
