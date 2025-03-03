import requests
import json
from datetime import datetime


def get_kinneret_levels(limit=10):
    """
    Retrieve Kinneret water level data from data.gov.il

    Parameters:
        limit (int): Number of records to return

    Returns:
        list: Records containing date and water level measurements
    """
    # The resource ID for the Kinneret water level dataset
    resource_id = "2de7b543-e13d-4e7e-b4c8-56071bc4d3c8"

    # Build the API URL
    base_url = 'https://data.gov.il/api/3/action/datastore_search'

    # Set up parameters - requesting a small number of records
    params = {
        'resource_id': resource_id,
        'limit': limit
    }

    try:
        # Make the request to the API
        response = requests.get(base_url, params=params)

        # Check if request was successful
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Check if the API request itself returned success
        if data.get('success', False):
            # Extract just the records portion of the response
            records = data.get('result', {}).get('records', [])
            return records
        else:
            print(f"API Error: {data.get('error', {})}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return []
    except json.JSONDecodeError:
        print("Error: Could not parse JSON response")
        return []


def format_date(date_str):
    """Convert date string to a more readable format"""
    try:
        # Try to parse the date string
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        # Return a more human-readable format
        return date_obj.strftime("%d/%m/%Y")
    except ValueError:
        # If parsing fails, return the original string
        return date_str


def print_kinneret_data(records):
    """Print Kinneret water level data in a readable format"""
    if not records:
        print("No data found.")
        return

    # Print header
    print("\n=== Kinneret Water Level Data ===")
    print(f"{'Survey Date':<12} | {'Water Level (m)':<15}")
    print("-" * 30)

    # Print each record
    for record in records:
        date = format_date(record.get('Survey_Date', 'N/A'))
        water_level = record.get('Kinneret_Level', 'N/A')
        print(f"{date:<12} | {water_level:<15}")


# Main execution
if __name__ == "__main__":
    # Get 10 records from the Kinneret dataset
    kinneret_data = get_kinneret_levels(10)

    # Print the data in a readable format
    print_kinneret_data(kinneret_data)

    # Also print the raw data for reference
    print("\nRaw data format:")
    for record in kinneret_data[:2]:  # Just show 2 records in raw format
        print(json.dumps(record, indent=2))