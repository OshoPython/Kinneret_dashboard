import requests
import json
from datetime import datetime


def get_all_kinneret_levels():
    """
    Retrieve all Kinneret water level data from data.gov.il

    Returns:
        list: Complete records of date and water level measurements
    """
    # The resource ID for the Kinneret water level dataset
    resource_id = "2de7b543-e13d-4e7e-b4c8-56071bc4d3c8"

    # Build the API URL
    base_url = 'https://data.gov.il/api/3/action/datastore_search'

    # Initialize variables for pagination
    all_records = []
    offset = 0
    batch_size = 1000  # Maximum records per request (API might have limits)
    total_records = None

    while True:
        # Set up parameters with pagination
        params = {
            'resource_id': resource_id,
            'limit': batch_size,
            'offset': offset
        }

        try:
            # Make the request to the API
            response = requests.get(base_url, params=params)

            # Check if request was successful
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()

            # Check if the API request itself returned success
            if not data.get('success', False):
                print(f"API Error: {data.get('error', {})}")
                break

            # Get this batch of records
            result = data.get('result', {})
            records = result.get('records', [])

            # If no records were returned, we're done
            if not records:
                break

            # Add these records to our collection
            all_records.extend(records)

            # Get the total number of records (if not already known)
            if total_records is None:
                total_records = result.get('total', 0)
                print(f"Total records in dataset: {total_records}")

            # Update offset for next batch
            offset += batch_size

            # Print progress
            print(f"Retrieved {len(all_records)} of {total_records} records...")

            # If we've retrieved all records, we're done
            if len(all_records) >= total_records:
                break

        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            break
        except json.JSONDecodeError:
            print("Error: Could not parse JSON response")
            break

    return all_records


def format_date(date_str):
    """Convert date string to a more readable format"""
    try:
        # The date format might vary, so try different formats
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")

        # Return a more human-readable format
        return date_obj.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        # If parsing fails, return the original string
        return date_str if date_str else "N/A"


def print_kinneret_data_sample(records, sample_size=20):
    """Print a sample of Kinneret water level data in a readable format"""
    if not records:
        print("No data found.")
        return

    # Print header
    print("\n=== Kinneret Water Level Data Sample ===")
    print(f"Showing {min(sample_size, len(records))} of {len(records)} records")
    print(f"{'Survey Date':<12} | {'Water Level (m)':<15}")
    print("-" * 30)

    # Determine the field names by looking at the first record
    # This makes the code more adaptable to actual field names
    first_record = records[0]
    date_field = next((field for field in first_record.keys() if 'date' in field.lower()), None)
    level_field = next((field for field in first_record.keys() if 'level' in field.lower()), None)

    if not date_field or not level_field:
        print("Could not identify date or level fields in the data.")
        print("Available fields:", list(first_record.keys()))
        return

    # Print a sample of records (start, middle, and end)
    if len(records) <= sample_size:
        sample = records
    else:
        # Take records from beginning, middle and end
        sample_per_section = sample_size // 3
        start = records[:sample_per_section]
        middle_idx = len(records) // 2
        middle = records[middle_idx:middle_idx + sample_per_section]
        end = records[-sample_per_section:]
        sample = start + middle + end

    # Print each record in the sample
    for record in sample:
        date = format_date(record.get(date_field, 'N/A'))
        water_level = record.get(level_field, 'N/A')
        print(f"{date:<12} | {water_level:<15}")


def analyze_kinneret_data(records):
    """Perform basic analysis on the Kinneret water level data"""
    if not records:
        print("No data found for analysis.")
        return

    # Determine the field names
    first_record = records[0]
    date_field = next((field for field in first_record.keys() if 'date' in field.lower()), None)
    level_field = next((field for field in first_record.keys() if 'level' in field.lower()), None)

    if not date_field or not level_field:
        print("Could not identify date or level fields for analysis.")
        return

    # Extract water levels, converting to float and filtering out non-numeric values
    water_levels = []
    for record in records:
        try:
            level = float(record.get(level_field, 'N/A'))
            water_levels.append(level)
        except (ValueError, TypeError):
            continue

    if not water_levels:
        print("No valid water level data found for analysis.")
        return

    # Calculate basic statistics
    min_level = min(water_levels)
    max_level = max(water_levels)
    avg_level = sum(water_levels) / len(water_levels)

    # Find records with min and max values
    min_record = next(r for r in records if float(r.get(level_field, 0)) == min_level)
    max_record = next(r for r in records if float(r.get(level_field, 0)) == max_level)

    # Print analysis results
    print("\n=== Kinneret Water Level Analysis ===")
    print(f"Total records analyzed: {len(water_levels)}")
    print(f"Minimum water level: {min_level} meters on {format_date(min_record.get(date_field, 'N/A'))}")
    print(f"Maximum water level: {max_level} meters on {format_date(max_record.get(date_field, 'N/A'))}")
    print(f"Average water level: {avg_level:.2f} meters")


# Main execution
if __name__ == "__main__":
    print("Retrieving all Kinneret water level data...")
    all_kinneret_data = get_all_kinneret_levels()

    if all_kinneret_data:
        print(f"\nSuccessfully retrieved {len(all_kinneret_data)} records!")

        # Store the data in a variable as requested
        kinneret_dataset = all_kinneret_data

        # Print a sample of the data
        print_kinneret_data_sample(kinneret_dataset)

        # Perform basic analysis
        analyze_kinneret_data(kinneret_dataset)

        # Show data structure by printing first record
        print("\nData structure (first record):")
        print(json.dumps(kinneret_dataset[0], indent=2, ensure_ascii=False))

        print("\nThe entire dataset is stored in the variable 'kinneret_dataset'")
        print("You can access any record with kinneret_dataset[index]")
    else:
        print("Failed to retrieve Kinneret water level data.")