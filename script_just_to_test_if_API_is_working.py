import requests
import pandas as pd
import time
from datetime import datetime


def test_kinneret_api():
    print("=== Testing Kinneret Water Level API ===")
    start_time = time.time()

    # The resource ID for the Kinneret water level dataset
    resource_id = "2de7b543-e13d-4e7e-b4c8-56071bc4d3c8"

    # Build the API URL
    base_url = 'https://data.gov.il/api/3/action/datastore_search'

    # First request to get total count
    params = {'resource_id': resource_id, 'limit': 1}
    print("Making initial API request to get record count...")
    initial_response = requests.get(base_url, params=params)
    initial_data = initial_response.json()

    if not initial_data.get('success', False):
        print(f"ERROR: API request failed: {initial_data.get('error', 'Unknown error')}")
        return None

    # Get total records count
    total_records = initial_data.get('result', {}).get('total', 0)
    print(f"Found {total_records} records in the dataset")

    # Retrieve all records
    all_records = []

    print(f"Requesting all {total_records} records at once...")
    params = {
        'resource_id': resource_id,
        'limit': total_records  # Try to get all at once
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data.get('success', False):
        all_records = data.get('result', {}).get('records', [])
        print(f"Successfully retrieved {len(all_records)} records")
    else:
        print(f"ERROR: {data.get('error', 'Unknown error')}")
        return None

    # Convert to DataFrame
    print("Converting to DataFrame...")
    df = pd.DataFrame(all_records)

    # Display column names
    print("\nColumns in API data:")
    for i, col in enumerate(df.columns):
        print(f"  {i}: \"{col}\"")

    # Identify date and level columns
    date_columns = [col for col in df.columns if any(term in col.lower() for term in ['date', 'survey', 'תאריך'])]
    level_columns = [col for col in df.columns if
                     any(term in col.lower() for term in ['level', 'kinneret', 'מפלס', 'כנרת'])]

    print("\nIdentified columns:")
    if date_columns:
        date_col = date_columns[0]
        print(f"  Date column: '{date_col}'")
        df['Survey_Date'] = df[date_col]
    else:
        print("  ERROR: Could not identify date column")

    if level_columns:
        level_col = level_columns[0]
        print(f"  Water level column: '{level_col}'")
        df['Kinneret_Level'] = pd.to_numeric(df[level_col], errors='coerce')
    else:
        print("  ERROR: Could not identify water level column")

    # Try different date formats
    date_formats = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
    date_conversion_succeeded = False

    for fmt in date_formats:
        try:
            df['date'] = pd.to_datetime(df['Survey_Date'], format=fmt)
            print(f"\nSuccessfully converted dates using format: {fmt}")
            date_conversion_succeeded = True
            break
        except Exception as e:
            print(f"  Date format {fmt} failed: {e}")

    if not date_conversion_succeeded:
        print("Trying automatic date parsing...")
        df['date'] = pd.to_datetime(df['Survey_Date'], errors='coerce')
        if df['date'].isna().sum() > 0:
            print(f"  Warning: {df['date'].isna().sum()} dates could not be parsed")
        else:
            print("  Date auto-detection successful")

    # Add required columns
    df['water_level'] = df['Kinneret_Level']
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    # Sort and clean
    df = df.sort_values('date')
    original_count = len(df)
    df = df.dropna(subset=['date', 'water_level'])
    if len(df) < original_count:
        print(f"\nDropped {original_count - len(df)} rows with missing data")

    df = df.reset_index(drop=True)

    # Display data summary
    print("\n=== Data Summary ===")
    print(f"Total records: {len(df)}")

    if not df.empty:
        print(f"Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
        print(f"Water level range: {df['water_level'].min():.2f} to {df['water_level'].max():.2f}")
        print(f"Average water level: {df['water_level'].mean():.2f}")

    # Display sample data
    print("\n=== Sample Data (First 5 Rows) ===")
    print(df.head().to_string())

    # Display data shape
    print("\n=== Data Shape ===")
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

    # Print column info
    print("\n=== Column Information ===")
    for col in df.columns:
        null_count = df[col].isna().sum()
        if pd.api.types.is_numeric_dtype(df[col]):
            print(f"{col}: Numeric, {null_count} nulls, Range: {df[col].min()} to {df[col].max()}")
        elif pd.api.types.is_datetime64_dtype(df[col]):
            print(f"{col}: DateTime, {null_count} nulls, Range: {df[col].min()} to {df[col].max()}")
        else:
            print(f"{col}: Object/String, {null_count} nulls")

    # Execution time
    elapsed_time = time.time() - start_time
    print(f"\nTotal execution time: {elapsed_time:.2f} seconds")

    return df


# Execute the test function
if __name__ == "__main__":
    print(f"Running test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    kinneret_data = test_kinneret_api()

    if kinneret_data is not None:
        # Additional analysis that you might want to perform
        print("\n=== Additional Analysis ===")

        # Check for outliers
        mean = kinneret_data['water_level'].mean()
        std = kinneret_data['water_level'].std()
        outliers = kinneret_data[(kinneret_data['water_level'] > mean + 3 * std) |
                                 (kinneret_data['water_level'] < mean - 3 * std)]

        if not outliers.empty:
            print(f"Found {len(outliers)} potential outliers (beyond 3 standard deviations)")
            print(outliers[['date', 'water_level']].head().to_string())
        else:
            print("No significant outliers detected")

        # Check data consistency
        yearly_counts = kinneret_data.groupby('year').size()
        print("\nRecords per year:")
        print(yearly_counts.to_string())

        # Years with less than 10 records might indicate missing data
        sparse_years = yearly_counts[yearly_counts < 10]
        if not sparse_years.empty:
            print("\nYears with potentially incomplete data (less than 10 records):")
            print(sparse_years.to_string())

        # Check for gaps in the data
        kinneret_data['days_since_prev'] = (kinneret_data['date'] -
                                            kinneret_data['date'].shift(1)).dt.days

        large_gaps = kinneret_data[kinneret_data['days_since_prev'] > 60]
        if not large_gaps.empty:
            print("\nLarge gaps in data (more than 60 days):")
            print(large_gaps[['date', 'days_since_prev', 'water_level']].head(10).to_string())

        print("\nTest completed successfully")