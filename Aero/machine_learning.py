from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
from sklearn.preprocessing import OneHotEncoder


def kmeans_dates(data):
    # Convert 'Cert Date' and 'Expiration Date' to datetime objects
    data['Certificate Issue Date'] = pd.to_datetime(data['Certificate Issue Date'])
    data['Expiration Date'] = pd.to_datetime(data['Expiration Date'])

    # Create a new dataframe with 'Cert Date' and 'Expiration Date' columns
    data_dates = data[['Certificate Issue Date', 'Expiration Date']]

    # Scale the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data_dates)

    # Perform K-means clustering
    kmeans = KMeans(n_clusters=3, n_init=10)
    kmeans.fit(scaled_data)

    # Assign the clusters to the data
    data['dates_cluster'] = kmeans.labels_
    return data


def kmeans_aircraft_info(data):
    # Select relevant columns
    data_cluster = data[['Manufacturer Name', 'Model', 'Type Engine']]
    
    # One hot encode categorical variables
    encoder = OneHotEncoder()
    encoded_data = encoder.fit_transform(data_cluster)
    
    # Perform K-means clustering
    kmeans = KMeans(n_clusters=3, n_init=10)
    kmeans.fit(encoded_data)
    
    # Assign the clusters to the data
    data['aircraft_cluster'] = kmeans.labels_

    return data


def kmeans_type(data):
    # Select relevant columns

    data_cluster = data[['Type Registration', 'Type Aircraft']]

    # One hot encode categorical variables
    encoder = OneHotEncoder()
    encoded_data = encoder.fit_transform(data_cluster)

    # Perform K-means clustering
    kmeans = KMeans(n_clusters=3, n_init=10)
    kmeans.fit(encoded_data)

    # Assign the clusters to the data
    data['type_cluster'] = kmeans.labels_

    return data
