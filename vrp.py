import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def read_file(filename):
    """
    Read coordinates and demand values from a file.
    For Excel files, specify the sheet name.
    Assumes the data is in columns labeled 'Latitude', 'Longitude', and 'Demand'.
    """
    df = pd.read_csv(filename)
    coordinates = df[['Latitude', 'Longitude']].values
    demands = df['Demand'].values

    return coordinates, demands, df



def calculate_distance_matrix(coordinates):
    """
    Calculate the distance matrix between coordinates.
    """
    num_points = len(coordinates)                       # Number of locations
    dist_matrix = np.zeros((num_points, num_points))    # Initialize distance matrix

    for i in range(num_points):
        for j in range(num_points):
            dist_matrix[i, j] = calculate_distance(coordinates, i, j)  # Calculate distance

    return dist_matrix


def calculate_distance(coordinates, i, j):
    """
    Calculate the Euclidean distance between two points.
    """
    x1, y1 = coordinates[i]
    x2, y2 = coordinates[j]
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)          # Use the Euclidean distance formula


def calculate_total_distance(route, dist_matrix):
    """
    Calculate the total distance of a given route using the distance matrix,
    including the return to the depot.
    """
    total_distance = 0
    num_points = len(route)

    for i in range(num_points - 1):
        current_node = route[i]
        next_node = route[i + 1]
        total_distance += dist_matrix[current_node, next_node]      # Sum up the distances between consecutive nodes

    return total_distance



def nearest_neighbor(dist_matrix, demands, capacity):
    """
    Apply the Nearest Neighbor heuristic to find initial routes for VRP.
    Ensures that trucks return to the depot after completing their route.
    """
    num_points = dist_matrix.shape[0]
    visited = np.zeros(num_points, dtype=bool)
    routes = []

    while np.sum(visited) < num_points - 1:            # Exclude the depot from this sum
        current_node = 0                               # Start at the depot (node 0)
        current_capacity = 0    
        route = [current_node]
        visited[current_node] = True

        while True:
            nearest = None
            min_dist = float('inf')

            for neighbor in np.where(~visited)[0]:
                if neighbor == 0:                      # Skip the depot in the nearest neighbor search
                    continue
                if demands[neighbor] + current_capacity <= capacity and dist_matrix[current_node, neighbor] < min_dist:
                    nearest = neighbor
                    min_dist = dist_matrix[current_node, neighbor]

            if nearest is None:                        # No valid neighbor found, route is full
                break

            route.append(nearest)
            visited[nearest] = True
            current_capacity += demands[nearest]
            current_node = nearest

        route.append(0)                                # Return to the depot at the end of the route
        routes.append(route)

    return routes


def format_output(routes):
    """
    Format the final routes as required.
    In this example, it returns a list of routes.
    """
    return routes


def vrp_solver(filename, capacity):
    """
    Solve the VRP using the provided filename for coordinates and vehicle capacity.
    """
    coordinates, demands, df = read_file(filename)
    dist_matrix = calculate_distance_matrix(coordinates)        # calculate distances between all nodes
    routes = nearest_neighbor(dist_matrix, demands, capacity)   # Generate routes using the Nearest Neighbor heuristic
    formatted_routes = format_output(routes)

    return formatted_routes, df


def format_output_with_cities(routes, df):
    """
    Format the routes to display city names instead of indices.
    
    :param routes: List of routes, where each route is a list of node indices.
    :param df: DataFrame containing the data, including the "City" column.
    :return: List of routes with city names.
    """
    city_routes = []
    city_names = df['City'].values

    for route in routes:
        city_route = [city_names[node] for node in route]       # Convert node indices to city names
        city_routes.append(city_route)

    return city_routes