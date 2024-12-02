from sklearn.cluster import KMeans
import numpy as np

def perform_clustering(data: list, num_clusters: int) -> dict:
    """
    Performs K-Means clustering on the given data.

    Args:
        data (list): A list of dictionaries where each dictionary represents a customer
                     and its numerical features (e.g., {'spend': 500, 'visits': 5}).
        num_clusters (int): Number of clusters to form.

    Returns:
        dict: A dictionary mapping each cluster to its customer indices.
    """
    if not data or not isinstance(data, list):
        raise ValueError("Data must be a non-empty list of dictionaries.")
    
    # Convert list of dictionaries to a NumPy array for clustering
    feature_matrix = np.array([list(customer.values()) for customer in data])

    # Perform K-Means clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(feature_matrix)

    # Assign customers to clusters
    cluster_labels = kmeans.labels_
    clustered_data = {i: [] for i in range(num_clusters)}
    for idx, cluster in enumerate(cluster_labels):
        clustered_data[cluster].append(data[idx])

    return clustered_data


# Example Usage (comment out for production)
if __name__ == "__main__":
    # Example customer data
    customers = [
        {"spend": 500, "visits": 10},
        {"spend": 300, "visits": 5},
        {"spend": 1000, "visits": 20},
        {"spend": 200, "visits": 3},
        {"spend": 800, "visits": 15},
        {"spend": 50, "visits": 1},
    ]

    # Perform clustering into 2 groups
    clusters = perform_clustering(customers, num_clusters=2)
    print("Clustered Data:")
    for cluster, members in clusters.items():
        print(f"Cluster {cluster}: {members}")
