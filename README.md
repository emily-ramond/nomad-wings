# NomadWings 🌴 Backpacker Assistant

## Overview
NomadWings is a domain-specific, web-based chat agent designed to help backpackers plan their trips to Southeast Asia (specifically Thailand and Vietnam). Planning a backpacking trip often requires juggling multiple tabs for flight aggregators, currency converters, and government visa portals. NomadWings solves this problem by centralizing these tasks into a single conversational interface. 

The agent utilizes the Gemini model and custom tool-calling to fetch live flight data, estimate local purchasing power, and check visa requirements—all while maintaining a savvy, budget-conscious travel persona.

## Sample Queries for Graders
To test the agent's tools and functionality, copy and paste the following three sample queries into the chat interface:

1. **Flight Search (External API):** 
   > *"Find cheap one-way flights from Bangkok to Ho Chi Minh City on 2026-11-15"*
2. **Budget Conversion (External API):** 
   > *"I have a $250 USD budget for Vietnam. How far will that go in hostel nights and street food meals?"*
3. **Visa Check (Local DB):** 
   > *"Do US passport holders need a visa for Thailand or Vietnam?"*

## Tools Implemented
This agent meets the requirement of implementing at least three tools, including original tools tailored to the backpacking domain:

1. `search_cheap_flights`: Calls the SerpApi Google Flights engine to fetch live, one-way flight prices and durations between two IATA airport codes[cite: 55].
2. `convert_backpacker_budget`: Calls the Open Access ExchangeRate-API to convert USD into local currency (THB or VND) and calculates estimated purchasing power based on backpacker benchmarks (e.g., hostel beds, street food).
3. `check_visa_requirements`: A local database tool that maps the user's passport nationality to specific tourist visa rules for Thailand and Vietnam, ensuring fast and rate-limit-free responses.

## Setup & Local Development

### Prerequisites
*   Python 3.10+
*   [`uv`](https://github.com/astral-sh/uv) package manager
*   Google Cloud SDK (`gcloud`)
*   SerpApi Key

### Running Locally
1. **Authenticate with Google Cloud:**
   ```bash
   gcloud auth application-default login