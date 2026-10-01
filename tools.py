"""The tools the harness can run, and the JSON that describes them to the model."""

import json
import os
import requests

# SerpApi Base URL
SERPAPI_URL = "https://serpapi.com/search"

def search_cheap_flights(departure_id: str, arrival_id: str, outbound_date: str) -> str:
    """Get live one-way flight prices using Google Flights via SerpApi."""
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        return json.dumps({"error": "SERPAPI_KEY is not set on the server."})

    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "type": "2",          
        "currency": "USD",
        "hl": "en",           
        "api_key": api_key
    }

    try:
        response = requests.get(SERPAPI_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        best_flights = data.get("best_flights", [])
        
        if not best_flights:
            return json.dumps({"error": f"No flights found from {departure_id} to {arrival_id} on {outbound_date}."})

        compact_results = []
        for flight in best_flights[:3]: 
            price = flight.get("price", "Unknown")
            flight_legs = flight.get("flights", [{}])
            airline = flight_legs[0].get("airline", "Unknown")
            duration = flight.get("total_duration", "Unknown")
            
            compact_results.append({
                "airline": airline,
                "price_usd": price,
                "duration_minutes": duration
            })
            
        return json.dumps({"flights": compact_results})

    except requests.RequestException as e:
        return json.dumps({"error": f"Flight API failed: {str(e)}"})


def convert_backpacker_budget(usd_amount: float, country: str) -> str:
    """Convert a USD budget into local currency (THB or VND) and calculate backpacker purchasing power."""
    try:
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        response.raise_for_status()
        rates = response.json().get("rates", {})
    except requests.RequestException as e:
        return json.dumps({"error": f"Currency API failed: {e}. Let the user know you cannot convert right now."})
        
    if country == "Thailand":
        local_currency = "THB"
        rate = rates.get("THB", 34.0) 
        local_amount = usd_amount * rate
        hostel_cost, street_food, beer_cost = 300, 60, 60
    elif country == "Vietnam":
        local_currency = "VND"
        rate = rates.get("VND", 25000.0)
        local_amount = usd_amount * rate
        hostel_cost, street_food, beer_cost = 150000, 50000, 20000
    else:
        return json.dumps({"error": "Unsupported country. Only Thailand and Vietnam are supported."})
        
    return json.dumps({
        "country": country,
        "usd_amount": usd_amount,
        "local_currency": local_currency,
        "local_amount": round(local_amount, 2),
        "purchasing_power_estimate": {
            "hostel_nights": int(local_amount // hostel_cost),
            "street_food_meals": int(local_amount // street_food),
            "local_beers": int(local_amount // beer_cost)
        }
    })


def check_visa_requirements(nationality: str, destination: str) -> str:
    """Check visa requirements for Thailand or Vietnam using a local database."""
    rules = {
        "Thailand": {
            "US": "Visa exempt for up to 60 days.",
            "UK": "Visa exempt for up to 60 days.",
            "EU": "Visa exempt for up to 60 days.",
            "Australia": "Visa exempt for up to 60 days.",
            "Canada": "Visa exempt for up to 60 days."
        },
        "Vietnam": {
            "US": "Requires an e-Visa (valid for up to 90 days). Apply online before arrival.",
            "UK": "Visa exempt for up to 45 days. E-visa required for longer stays.",
            "EU": "Visa exempt for up to 45 days (for most EU nations). E-visa for longer.",
            "Australia": "Requires an e-Visa (valid for up to 90 days). Apply online before arrival.",
            "Canada": "Requires an e-Visa (valid for up to 90 days). Apply online before arrival."
        }
    }
    
    try:
        rule = rules[destination][nationality]
        return json.dumps({
            "destination": destination, 
            "nationality": nationality, 
            "visa_rule": rule
        })
    except KeyError:
        return json.dumps({"error": f"Visa data not found for nationality '{nationality}' traveling to '{destination}'."})


# What the model sees: the strict JSON schema describing your tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_cheap_flights",
            "description": "Find live one-way flight prices and options between two airports.",
            "parameters": {
                "type": "object",
                "properties": {
                    "departure_id": {
                        "type": "string", 
                        "description": "Origin airport 3-letter IATA code (e.g., 'JFK', 'BKK')"
                    },
                    "arrival_id": {
                        "type": "string", 
                        "description": "Destination airport 3-letter IATA code (e.g., 'SGN')"
                    },
                    "outbound_date": {
                        "type": "string", 
                        "description": "Departure date strictly in YYYY-MM-DD format"
                    }
                },
                "required": ["departure_id", "arrival_id", "outbound_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_backpacker_budget",
            "description": "Convert a USD budget into local currency and calculate how many hostel nights, local meals, and beers it buys.",
            "parameters": {
                "type": "object",
                "properties": {
                    "usd_amount": {
                        "type": "number", 
                        "description": "The amount in USD to convert"
                    },
                    "country": {
                        "type": "string", 
                        "description": "The destination country",
                        "enum": ["Thailand", "Vietnam"]
                    }
                },
                "required": ["usd_amount", "country"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_visa_requirements",
            "description": "Check the tourist visa rules for a specific nationality traveling to Thailand or Vietnam.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nationality": {
                        "type": "string", 
                        "description": "The passport country of the user",
                        "enum": ["US", "UK", "EU", "Australia", "Canada"]
                    },
                    "destination": {
                        "type": "string", 
                        "description": "The destination country",
                        "enum": ["Thailand", "Vietnam"]
                    }
                },
                "required": ["nationality", "destination"],
            },
        },
    }
]

# What the harness runs: tool name mapped to the Python function
TOOL_MAP = {
    "search_cheap_flights": search_cheap_flights,
    "convert_backpacker_budget": convert_backpacker_budget,
    "check_visa_requirements": check_visa_requirements
}

def run_tool(name: str, args: dict) -> str:
    """Run one tool call."""
    if name not in TOOL_MAP:
        return json.dumps({"error": f"Unknown tool '{name}'. Available: {list(TOOL_MAP)}"})
    try:
        return TOOL_MAP[name](**args)
    except TypeError as e:
        return json.dumps({"error": f"Bad arguments for {name}: {e}"})