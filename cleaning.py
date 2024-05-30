import pandas as pd

# Load the Airbnb dataset
def load_data(file_path):
    return pd.read_json(file_path)

# Preprocess the data
def preprocess_data(df):
    # Extract latitude and longitude coordinates
    df['latitude'] = df['address'].apply(lambda x: x['location']['coordinates'][1])
    df['longitude'] = df['address'].apply(lambda x: x['location']['coordinates'][0])
    
    # Convert price to float
    df['price'] = df['price'].apply(lambda x: float(x['$numberDouble']) if isinstance(x, dict) and '$numberDouble' in x else x)
    
    # Convert last_scraped to datetime and extract month
    df['last_scraped'] = pd.to_datetime(df['last_scraped'], errors='coerce')
    df['month'] = df['last_scraped'].dt.month
    
    # Extract other fields
    df['country_code'] = df['address'].apply(lambda x: x['country_code'])
    df['suburb'] = df['address'].apply(lambda x: x.get('suburb', 'Unknown'))
    
    # Assign rating based on number of reviews
    def assign_rating(num_reviews):
        if num_reviews <= 50:
            return 5
        elif num_reviews <= 100:
            return 6
        elif num_reviews <= 150:
            return 7
        elif num_reviews <= 200:
            return 8
        elif num_reviews <= 250:
            return 9
        else:
            return 10
    
    if 'number_of_reviews' in df.columns:
        df['rating'] = df['number_of_reviews'].apply(assign_rating)
    else:
        df['rating'] = float('nan')
    
    # Check if availability_30 exists
    df['availability'] = df['availability_30'] if 'availability_30' in df.columns else float('nan')
    
    # Extract additional fields
    df['city'] = df['address'].apply(lambda x: x.get('city', 'Unknown'))
    df['minimum_nights'] = df['minimum_nights'] if 'minimum_nights' in df.columns else float('nan')
    df['maximum_nights'] = df['maximum_nights'] if 'maximum_nights' in df.columns else float('nan')
    df['room_type'] = df['room_type'] if 'room_type' in df.columns else 'Unknown'
    df['bedrooms'] = df['bedrooms'] if 'bedrooms' in df.columns else float('nan')
    df['bathrooms'] = df['bathrooms'] if 'bathrooms' in df.columns else float('nan')
    df['amenities_count'] = df['amenities'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    df['number_of_reviews'] = df['number_of_reviews'] if 'number_of_reviews' in df.columns else 0

    return df[['latitude', 'longitude', 'name', 'price', 'property_type', 'month', 'country_code', 'suburb', 'rating',
               'city', 'availability', 'minimum_nights', 'maximum_nights', 'room_type', 'bedrooms', 'bathrooms', 
               'amenities_count', 'number_of_reviews']]

# Main function to load, preprocess, and save data
def main():
    # Load the data
    data = load_data(r'C:\Users\Ab Deshmukh\Desktop\Python\VSCode\airbnb.json')
    
    # Preprocess the data
    df = preprocess_data(data)
    
    # Save the cleaned data to a CSV file
    df.to_csv(r'C:\Users\Ab Deshmukh\Desktop\Python\VSCode\airbnb_cleaned.csv', index=False)
    print("Data cleaned and saved to 'airbnb_cleaned.csv'")

if __name__ == "__main__":
    main()
