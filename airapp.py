import streamlit as st
import pandas as pd
import plotly.express as px

# Load the Airbnb dataset
@st.cache_data
def load_data():
    return pd.read_json(ur file path')

# Preprocess the data
def preprocess_data(df):
    df['latitude'] = df['address'].apply(lambda x: x['location']['coordinates'][1] if x and 'location' in x else None)
    df['longitude'] = df['address'].apply(lambda x: x['location']['coordinates'][0] if x and 'location' in x else None)
    df['price'] = df['price'].apply(lambda x: float(x['$numberDouble']) if isinstance(x, dict) and '$numberDouble' in x else x)
    df['month'] = pd.to_datetime(df['last_scraped']).dt.month
    df['country_code'] = df['address'].apply(lambda x: x['country_code'] if x and 'country_code' in x else None)
    df['suburb'] = df['address'].apply(lambda x: x['suburb'] if x and 'suburb' in x else None)
    df['num_reviews'] = df['number_of_reviews'].apply(lambda x: int(x['$numberInt']) if isinstance(x, dict) and '$numberInt' in x else x)

    # Fill in ratings based on the number of reviews
    def determine_rating(num_reviews):
        if num_reviews <= 50:
            return 5
        elif 50 < num_reviews <= 100:
            return 6
        elif 100 < num_reviews <= 150:
            return 7
        elif 150 < num_reviews <= 200:
            return 8
        elif 200 < num_reviews <= 250:
            return 9
        else:
            return 10

    df['rating'] = df['num_reviews'].apply(determine_rating)

    # Extracting beds and bathrooms if they exist
    df['beds'] = df['beds'].apply(lambda x: int(x['$numberInt']) if isinstance(x, dict) and '$numberInt' in x else x)
    df['bathrooms'] = df['bathrooms'].apply(lambda x: float(x['$numberDouble']) if isinstance(x, dict) and '$numberDouble' in x else x)

    df.dropna(subset=['latitude', 'longitude', 'suburb', 'price'], inplace=True)
    return df[['latitude', 'longitude', 'name', 'price', 'property_type', 'month', 'country_code', 'suburb', 'rating', 'beds', 'bathrooms']]

# Aggregate data by location
def aggregate_location_data(df):
    aggregated_data = df.groupby(['suburb', 'country_code']).agg({
        'price': 'mean',
        'latitude': 'first',
        'longitude': 'first',
        'rating': 'mean',
        'beds': 'mean',
        'bathrooms': 'mean'
    }).reset_index()

    # Convert beds and bathrooms to whole numbers
    aggregated_data['beds'] = aggregated_data['beds'].round().astype(int)
    aggregated_data['bathrooms'] = aggregated_data['bathrooms'].round().astype(int)

    return aggregated_data

# Create the map with a bright color scheme
def create_map(df):
    fig = px.scatter_mapbox(
        df, 
        lat="latitude", 
        lon="longitude", 
        hover_name="name", 
        hover_data={"price": True, "beds": True, "bathrooms": True, "rating": True},
        color_continuous_scale=px.colors.sequential.Viridis, 
        color="price", 
        zoom=10, 
        height=600
    )
    fig.update_layout(mapbox_style="open-street-map")
    return fig

# Create the box plot for price vs. property type with log scale and enhanced hover info
def create_box_plot(df):
    fig = px.box(
        df, 
        x='property_type', 
        y='price', 
        title='Price Distribution by Property Type',
        labels={'price': 'Price ($)'}, 
        log_y=True,
        hover_data={'country_code': True, 'suburb': True, 'beds': True, 'bathrooms': True, 'rating': True}
    )
    return fig

# Create the bubble map for location-based price insights
def create_bubble_map(df):
    fig = px.scatter_mapbox(
        df, 
        lat="latitude", 
        lon="longitude", 
        size="price", 
        color="price",
        hover_name="suburb",
        hover_data={"price": True, "beds": True, "bathrooms": True, "rating": True},
        zoom=10, 
        height=600,
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig.update_layout(mapbox_style="open-street-map")
    return fig

def main():
    st.title('Airbnb Data Analysis and Visualization')

    # Load the data
    data = load_data()

    # Preprocess the data
    df = preprocess_data(data)

    # Display the first few rows of the preprocessed data for debugging
    st.write("First few rows of the preprocessed data:")
    st.write(df.head())

    # Selection for analysis type
    analysis_type = st.selectbox("Select Analysis Type", ["Geospatial Visualization", "Price vs Property Type", "Location-Based Price Insights"])

    if analysis_type == "Geospatial Visualization":
        # Country filter
        country_filter = st.selectbox("Select Country", options=list(df['country_code'].unique()) + ["All"])
        if country_filter == "All":
            df_country_filtered = df
        else:
            df_country_filtered = df[df['country_code'] == country_filter]

        # Suburb filter
        suburb_filter = st.multiselect("Select Suburb(s)", options=df_country_filtered['suburb'].unique(), default=df_country_filtered['suburb'].unique())
        price_range = st.slider("Select Price Range", min_value=float(df_country_filtered['price'].min()), max_value=float(df_country_filtered['price'].max()), value=(float(df_country_filtered['price'].min()), float(df_country_filtered['price'].max())))

        # Filter data
        filtered_data = df_country_filtered[(df_country_filtered['suburb'].isin(suburb_filter)) & (df_country_filtered['price'].between(price_range[0], price_range[1]))]

        # Display the map
        st.plotly_chart(create_map(filtered_data))

    elif analysis_type == "Price vs Property Type":
        # Box plot for price vs. property type
        st.plotly_chart(create_box_plot(df))

    elif analysis_type == "Location-Based Price Insights":
        # Aggregate data by location
        aggregated_data = aggregate_location_data(df)
        
        # Country filter
        country_filter = st.selectbox("Select Country", options=list(aggregated_data['country_code'].unique()) + ["All"])
        if country_filter == "All":
            aggregated_data_country_filtered = aggregated_data
        else:
            aggregated_data_country_filtered = aggregated_data[aggregated_data['country_code'] == country_filter]

        # Suburb filter
        suburb_filter = st.multiselect("Select Suburb(s)", options=aggregated_data_country_filtered['suburb'].unique(), default=aggregated_data_country_filtered['suburb'].unique())
        price_range = st.slider("Select Price Range", min_value=float(aggregated_data_country_filtered['price'].min()), max_value=float(aggregated_data_country_filtered['price'].max()), value=(float(aggregated_data_country_filtered['price'].min()), float(aggregated_data_country_filtered['price'].max())))

        # Filter aggregated data
        filtered_aggregated_data = aggregated_data_country_filtered[(aggregated_data_country_filtered['suburb'].isin(suburb_filter)) & (aggregated_data_country_filtered['price'].between(price_range[0], price_range[1]))]

        # Bubble map for location-based price insights
        st.plotly_chart(create_bubble_map(filtered_aggregated_data))

if __name__ == "__main__":
    main()
