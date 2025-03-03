import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from PIL import Image
import io
import requests


# Page configuration
st.set_page_config(
    page_title="Sea of Galilee Waterrr Level Monitor",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f0f8ff;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #1e3d59;
    }
    .highlight {
        background-color: rgba(144, 238, 144, 0.2);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .footer {
        margin-top: 30px;
        text-align: center;
        color: #666;
    }
    .metric-card {
        background-color: light-blue;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin: 10px;
    }

    /* This specifically targets the date text in the slider */
    .stSlider [data-testid="stThumbValue"] {
        color: #4682B4 !important; /* Steel Blue - change to any color you prefer */
        font-weight: 500; /* Optional: make the text slightly bolder */
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("Sea of Galilee Water Level Monitor")


# Sidebar


# Sidebar
st.sidebar.header("About")

# Profile picture (circular and centered)
profile_url = "https://media.licdn.com/dms/image/v2/D4E03AQHM2iVNATNcdg/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1705672518081?e=1746057600&v=beta&t=GVuWbbGddqgfidw2aemUaJGXSlWGk1LfaHTgXEXnSc8"

st.sidebar.markdown(
    f"""
    <div style="display: flex; justify-content: center;">
        <img src="{profile_url}" width="150" style="border-radius: 50%;">
    </div>
    """,
    unsafe_allow_html=True,
)

# Description text
st.sidebar.markdown(
    """    
    """
)
st.sidebar.markdown(
    """    
    The Sea of Galilee (Lake Kinneret) is Israel's largest freshwater lake and an important 
    water resource. This dashboard visualizes historical water level data, helping to understand 
    patterns and trends over time.    
    """
)

# Social Media Links
github_url = "https://github.com/oshopython"
linkedin_url = "https://www.linkedin.com/in/dor-gez-36aa02261/"
website_url = "https://oshopython.github.io/"
youtube_url = "https://www.youtube.com/@DorHydro"
email_address = "dorhydro@gmail.com"

st.sidebar.markdown(
    f"""
    <div style="display: flex; justify-content: center; gap: 20px; padding-top: 10px;">
        <a href="{github_url}" target="_blank">
            <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" width="30">
        </a>
        <a href="{linkedin_url}" target="_blank">
            <img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" width="30">
        </a>
        <a href="{website_url}" target="_blank">
            <img src="https://cdn-icons-png.flaticon.com/512/841/841364.png" width="30">
        </a>
        <a href="{youtube_url}" target="_blank">
            <img src="https://upload.wikimedia.org/wikipedia/commons/e/ef/Youtube_logo.png" width="30">
        </a>
        <a href="mailto:{email_address}">
            <img src="https://upload.wikimedia.org/wikipedia/commons/4/4e/Gmail_Icon.png" width="30">
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

# Load example data (replace with your actual data loading code)

#def load_data():
    # try:
    #     # Read the CSV file (adjust the path if needed)
    #     df = pd.read_csv('water_level.csv')
    #
    #     # Make sure the column names match what's in your CSV
    #     # If your columns are named differently, rename them here
    #     df.columns = ['Survey_Date', 'Kinneret_Level']
    #
    #     # Convert dates to datetime format for proper handling
    #     df['date'] = pd.to_datetime(df['Survey_Date'], format='%d/%m/%Y')
    #
    #     # Add water_level column that matches the naming used in the rest of the code
    #     df['water_level'] = df['Kinneret_Level']
    #
    #     # Add year and month columns which are used for different visualizations
    #     df['year'] = df['date'].dt.year
    #     df['month'] = df['date'].dt.month
    #
    #     # Sort by date (oldest to newest)
    #     df = df.sort_values('date')
    #
    #     # Reset index after sorting
    #     df = df.reset_index(drop=True)
    #
    #     return df
    #
    # except Exception as e:
    #     st.error(f"Error loading data: {e}")
    #     # Return empty dataframe with expected columns as fallback
    #     return pd.DataFrame(columns=['date', 'water_level', 'year', 'month'])

@st.cache_data(ttl=3600)  # Cache for 1 hour in production
def load_data():
    try:
        # The resource ID for the Kinneret water level dataset
        resource_id = "2de7b543-e13d-4e7e-b4c8-56071bc4d3c8"

        # Build the API URL
        base_url = 'https://data.gov.il/api/3/action/datastore_search'

        # Initialize variables for pagination
        all_records = []
        offset = 0
        batch_size = 1000  # Maximum records per request

        # First request to get total count (without displaying info)
        params = {'resource_id': resource_id, 'limit': 1}
        initial_response = requests.get(base_url, params=params)
        initial_data = initial_response.json()

        if not initial_data.get('success', False):
            raise Exception("API request was not successful")

        # Get total records count
        total_records = initial_data.get('result', {}).get('total', 0)

        # If no records, raise exception
        if total_records == 0:
            raise Exception("No records found in the dataset")

        # Retrieve all records
        if total_records <= 32000:
            # Get all at once
            params = {
                'resource_id': resource_id,
                'limit': total_records
            }

            response = requests.get(base_url, params=params)
            data = response.json()

            if data.get('success', False):
                all_records = data.get('result', {}).get('records', [])
            else:
                raise Exception(f"API Error: {data.get('error', {})}")
        else:
            # Use pagination for very large datasets
            while offset < total_records:
                params = {
                    'resource_id': resource_id,
                    'limit': batch_size,
                    'offset': offset
                }

                response = requests.get(base_url, params=params)
                data = response.json()

                if not data.get('success', False):
                    raise Exception(f"API Error at offset {offset}: {data.get('error', {})}")

                batch_records = data.get('result', {}).get('records', [])
                if not batch_records:
                    break

                all_records.extend(batch_records)
                offset += len(batch_records)

        # Convert to DataFrame
        df = pd.DataFrame(all_records)

        # Process column names without displaying debug info
        date_columns = [col for col in df.columns if any(term in col.lower() for term in ['date', 'survey', 'תאריך'])]
        level_columns = [col for col in df.columns if
                         any(term in col.lower() for term in ['level', 'kinneret', 'מפלס', 'כנרת'])]

        if date_columns:
            date_col = date_columns[0]
            df['Survey_Date'] = df[date_col]
        else:
            raise Exception("Date column not found")

        if level_columns:
            level_col = level_columns[0]
            df['Kinneret_Level'] = pd.to_numeric(df[level_col], errors='coerce')
        else:
            raise Exception("Water level column not found")

        # Convert dates to datetime - try multiple formats without displaying debug info
        date_formats = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']

        for fmt in date_formats:
            try:
                df['date'] = pd.to_datetime(df['Survey_Date'], format=fmt)
                break
            except:
                continue

        if 'date' not in df.columns or df['date'].isna().all():
            # Last resort - try pandas automatic parsing
            df['date'] = pd.to_datetime(df['Survey_Date'], errors='coerce')

        # Add water_level column for consistency with existing code
        df['water_level'] = df['Kinneret_Level']

        # Add year and month columns
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month

        # Sort by date (oldest to newest)
        df = df.sort_values('date')

        # Drop rows with missing key data
        df = df.dropna(subset=['date', 'water_level'])

        # Reset index after sorting and filtering
        df = df.reset_index(drop=True)

        return df

    except Exception as e:
        # Silently fall back to local CSV without showing error messages
        try:
            df = pd.read_csv('water_level.csv')

            if 'date' not in df.columns and 'Survey_Date' in df.columns:
                df['date'] = pd.to_datetime(df['Survey_Date'], errors='coerce')

            if 'water_level' not in df.columns and 'Kinneret_Level' in df.columns:
                df['water_level'] = df['Kinneret_Level']

            if 'year' not in df.columns:
                df['year'] = df['date'].dt.year
            if 'month' not in df.columns:
                df['month'] = df['date'].dt.month

            df = df.sort_values('date').reset_index(drop=True)

            return df

        except Exception:
            return pd.DataFrame(columns=['date', 'water_level', 'year', 'month', 'Survey_Date', 'Kinneret_Level'])


def check_api_status():

    """Check if the data.gov.il API is responding correctly"""
    try:
        # The resource ID for the Kinneret water level dataset
        resource_id = "2de7b543-e13d-4e7e-b4c8-56071bc4d3c8"

        # Build a simple API request (just asking for 1 record to minimize data transfer)
        base_url = 'https://data.gov.il/api/3/action/datastore_search'
        params = {'resource_id': resource_id, 'limit': 1}

        # Try to connect to the API with a short timeout
        response = requests.get(base_url, params=params, timeout=5)

        # Check if request was successful and returned valid JSON
        if response.status_code == 200 and response.json().get('success', False):
            return True
        return False
    except:
        # Any exception means the API is not working
        return False


# Add this in your sidebar section
# Assuming you already have a sidebar with other content

# Check API status and display indicator
api_status = check_api_status()

if api_status:
    st.sidebar.markdown(
        """
        <div style="
            background-color: #d4edda; 
            color: #155724; 
            padding: 10px; 
            border-radius: 5px; 
            margin-top: 20px;  /* This adds space above the box */
            margin-bottom: 15px; 
            display: flex; 
            align-items: center;
            font-weight: 500;
        ">
            <span style="
                background-color: #28a745; 
                height: 10px; 
                width: 10px; 
                border-radius: 50%; 
                display: inline-block; 
                margin-right: 8px;
            "></span>
            API Connected
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        """
        <div style="
            background-color: #f8d7da; 
            color: #721c24; 
            padding: 10px; 
            border-radius: 5px; 
            margin-top: 20px;  /* This adds space above the box */
            margin-bottom: 15px; 
            display: flex; 
            align-items: center;
            font-weight: 500;
        ">
            <span style="
                background-color: #dc3545; 
                height: 10px; 
                width: 10px; 
                border-radius: 50%; 
                display: inline-block; 
                margin-right: 8px;
            "></span>
            API Disconnected
        </div>
        """,
        unsafe_allow_html=True
    )

df = load_data()

# Calculate the min and max values with some padding
min_level = min(df['water_level'].min() - 0.5, -213.5)  # Ensure lower red line is visible
max_level = max(df['water_level'].max() + 0.5, -207.5)  # Ensure upper red line is visible
upper_threshold = df['water_level'].quantile(0.9)  # 90th percentile
lower_threshold = df['water_level'].quantile(0.1)  # 10th percentile
# Get the most recent date and reading
latest_date = df['date'].max()
latest_reading = df.loc[df['date'] == latest_date, 'water_level'].iloc[0]
# Get the date from one year ago
one_year_ago = latest_date - pd.DateOffset(years=1)
# Tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["Main Dashboard", "Historical Analysis", "Seasonal Patterns"])
# newest date
latest_date = df['date'].max().strftime('%d/%m/%Y')
latest_date_str = str(df['date'].max())
date_only = latest_date_str[:10]



with tab1:
    # Get current metrics with more robust calculations
    current_level = df['water_level'].iloc[-1]

    # Daily change (checks if we have yesterday's reading)
    if len(df) > 1:
        daily_change = df['water_level'].iloc[-1] - df['water_level'].iloc[-2]
    else:
        daily_change = 0

    # Get the most recent date and reading
    latest_date = df['date'].max()

    # Monthly change - find reading from about a month ago
    one_month_ago = latest_date - pd.DateOffset(months=1)
    month_old_data = df[df['date'] <= one_month_ago]
    if not month_old_data.empty:
        monthly_change = current_level - month_old_data['water_level'].iloc[-1]
    else:
        monthly_change = 0

    # Yearly change - find reading from about a year ago
    one_year_ago = latest_date - pd.DateOffset(years=1)
    year_old_data = df[df['date'] <= one_year_ago]
    if not year_old_data.empty:
        yearly_change = current_level - year_old_data['water_level'].iloc[-1]
    else:
        yearly_change = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Current Level", f"{current_level:.2f}m")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Daily Change", f"{daily_change:.2f}m", delta=f"{daily_change:.2f}m")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Last Monthly Change", f"{monthly_change:.2f}m", delta=f"{monthly_change:.2f}m")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Last Year Change", f"{yearly_change:.2f}m", delta=f"{yearly_change:.2f}m")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="text-align: right; color: #666; padding: 10px; font-size: 0.9em;">Last Updated: <strong>{date_only}</strong></div>',
        unsafe_allow_html=True)

    # Add Sea of Galilee image (you'll need to replace with your actual image)
    st.markdown("### Sea of Galilee")
    st.image(
        "Bathymetric_map_of_Sea_of_Galilee_no_background.jpg",
        caption="View of the Sea of Galilee", use_container_width=True)

    # Main visualization
    st.markdown("### Water Level Trend")

    # Date range slider
    date_range = st.slider(
        "Select Date Range",
        min_value=df['date'].min().date(),
        max_value=df['date'].max().date(),
        value=(df['date'].min().date(), df['date'].max().date())
    )

    # Filter data based on selected date range
    mask = (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])
    filtered_df = df.loc[mask]

    # Create interactive plot with Plotly
    fig = px.line(
        filtered_df,
        x='date',
        y='water_level',
        labels={'date': 'Date', 'water_level': 'Water Level (meters above sea level)'},
        title=f"Water Level Trend ({date_range[0]} to {date_range[1]})"
    )

    # Add reference lines for important thresholds
    fig.add_hline(y=-208.8, line_dash="dot", line_color="red",
                  annotation_text="Upper Red Line (-208.8m)", annotation_position="top right")
    fig.add_hline(y=-213.0, line_dash="dash", line_color="red",
                  annotation_text="Lower Red Line (-213.0m)", annotation_position="bottom right")
    fig.add_hline(y=-214.87, line_dash="dot", line_color="black",
                  annotation_text="Black Line (-214.87m)", annotation_position="bottom right")
    # # Add annotation for historical context
    # if date_range[0] <= datetime(2018, 1, 1).date() <= date_range[1]:
    #     fig.add_vline(x=datetime(2018, 1, 1), line_dash="dot", line_color="gray")
    #     fig.add_annotation(x=datetime(2018, 1, 1), y=-215,
    #                        text="Drought Period", showarrow=True, arrowhead=1)

    # Update layout for better appearance
    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor="rgba(240, 248, 255, 0.5)",
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
            range=[min_level, max_level]  # Set dynamic range that includes both red lines
        ),
        height=500
    )

    # Make the line smoother and more attractive
    fig.update_traces(
        line=dict(width=3, color='rgba(0, 128, 255, 0.8)'),
        mode='lines'
    )

    # Add water level fill
    fig.add_trace(
        go.Scatter(
            x=filtered_df['date'],
            y=filtered_df['water_level'],
            fill='tozeroy',
            fillcolor='rgba(0, 128, 255, 0.2)',
            line=dict(color='rgba(255, 255, 255, 0)'),
            showlegend=False
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Information box
    st.markdown("""
    <div class="highlight">
        <h3>Water Level Key Notes</h3>
        <p>The Sea of Galilee's water level is measured in meters below sea level:</p>
        <ul>
            <li><strong>Upper Red Line (-208.8m):</strong> When the water level rises above this, water must be released to prevent flooding.</li>
            <li><strong>Lower Red Line (-213.0m):</strong> Below this level, water pumping is prohibited to protect the ecosystem.</li>
            <li><strong>Black Line (-214.87m):</strong> Pumping is not allowed even for drinking water.
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("## Historical Water Level Analysis")

    # Year comparison
    st.markdown("### Compare Years")

    # Select years to compare
    years = sorted(df['year'].unique())
    selected_years = st.multiselect(
        "Select years to compare",
        options=years,
        default=years[-5:]  # Default to most recent 5 years
    )

    if selected_years:
        # Create an empty list to hold data for each selected year
        yearly_data = []

        # Process each selected year individually
        for year in selected_years:
            # Filter data for just this specific year
            year_df = df[df['year'] == year].copy()

            # Skip if no data for this year
            if len(year_df) == 0:
                st.warning(f"No data available for year {year}")
                continue

            # Reset day to enable comparison between leap and non-leap years
            year_df['day_of_year'] = year_df['date'].dt.dayofyear

            # Add to our collection
            yearly_data.append(year_df)

        # Only proceed if we have data to show
        if yearly_data:
            yearly_comparison = pd.concat(yearly_data)

            # Create comparison chart
            fig = px.line(
                yearly_comparison,
                x='day_of_year',
                y='water_level',
                color='year',
                labels={'day_of_year': 'Day of Year', 'water_level': 'Water Level (m)', 'year': 'Year'},
                title="Year-over-Year Comparison"
            )

            # Update layout for better visualization
            min_level = yearly_comparison['water_level'].min() - 0.5
            max_level = yearly_comparison['water_level'].max() + 0.5

            fig.update_layout(
                hovermode="x unified",
                plot_bgcolor="rgba(240, 248, 255, 0.5)",
                height=500,
                yaxis=dict(
                    range=[min_level, max_level],
                    title="Water Level (meters)"
                ),
                xaxis=dict(
                    title="Day of Year",
                    tickmode='array',
                    tickvals=[1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335],
                    ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                ),
                legend=dict(
                    title="Year",
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            # Add better month labels for readability
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No data available for the selected years. Please choose different years.")
    else:
        st.info("Please select at least one year to display data.")

with tab3:
    st.markdown("## Seasonal Patterns")

    # Calculate monthly averages across all years
    monthly_avg = df.groupby('month')['water_level'].mean().reset_index()
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_avg['month_name'] = monthly_avg['month'].apply(lambda x: month_names[x - 1])

    # Create seasonal pattern chart
    fig = px.line(
        monthly_avg,
        x='month',
        y='water_level',
        labels={'month': 'Month', 'water_level': 'Average Water Level (m)'},
        title="Average Monthly Water Levels (All Years)"
    )

    # Customize x-axis to show month names
    fig.update_xaxes(
        tickvals=list(range(1, 13)),
        ticktext=month_names
    )

    # Update layout for better appearance
    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor="rgba(240, 248, 255, 0.5)",
        height=500,
        yaxis=dict(range=[min(monthly_avg['water_level']) - 0.5, max(monthly_avg['water_level']) + 0.5])
    )

    # Make the line smoother and more attractive
    fig.update_traces(
        line=dict(width=3, color='rgba(0, 128, 255, 0.8)'),
        mode='lines+markers'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Seasonal heatmap
    st.markdown("### Seasonal Heatmap")

    # Pivot data to create year x month heatmap
    pivot_df = df.pivot_table(
        index='year',
        columns='month',
        values='water_level',
        aggfunc='mean'
    )

    # Create heatmap
    fig = px.imshow(
        pivot_df,
        labels=dict(x="Month", y="Year", color="Water Level (m)"),
        x=[month_names[i - 1] for i in pivot_df.columns],
        y=pivot_df.index,
        color_continuous_scale="Blues_r",  # Reversed blue scale (darker = lower)
        title="Water Level Heatmap by Year and Month"
    )

    fig.update_layout(
        height=600,
        coloraxis_colorbar=dict(
            title="Water Level (m)",
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Seasonal explanation
    st.markdown("""
    <div class="highlight">
        <h3>Understanding Seasonal Patterns</h3>
        <p>The Sea of Galilee's water level follows a seasonal pattern influenced by:</p>
        <ul>
            <li><strong>Winter Rains (November-March):</strong> The primary source of water influx, causing levels to rise.</li>
            <li><strong>Dry Summer (May-October):</strong> Increased evaporation and water usage leads to declining levels.</li>
            <li><strong>Spring Runoff (March-April):</strong> Melting snow from Mount Hermon provides additional water input.</li>
        </ul>
        <p>These natural cycles, combined with water management decisions, create the annual patterns visible in the data.</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>Data sourced from Israeli water authority | Dor G ©</p>
    
</div>
""", unsafe_allow_html=True)