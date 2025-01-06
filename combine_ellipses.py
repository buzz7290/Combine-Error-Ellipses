import numpy as np
import copy
import convert_coordinates as cc

def compute_diagonal_matrix(semi_major_axis, semi_minor_axis):
    """Calculate the diagonal matrix D using constant chi_squared."""
    chi_squared = 5.99
    a = semi_major_axis
    b = semi_minor_axis
    D = np.diag([a**2 / chi_squared, b**2 / chi_squared])
    return D

def compute_rotation_matrix(theta):
    """Calculate the rotation matrix V."""
    theta=90-theta
    theta_rad = np.radians(theta)
    V = np.array([
        [np.cos(theta_rad), -np.sin(theta_rad)],
        [np.sin(theta_rad), np.cos(theta_rad)]
    ])
    return V

def inverse_2x2_matrix(matrix):
    """
    Calculate the inverse of a 2x2 matrix.

    Parameters:
    matrix: list : A 2x2 matrix represented as a list of lists.

    Returns:
    list : The inverse of the matrix if it exists, otherwise None.
    """
    if len(matrix) != 2 or len(matrix[0]) != 2:
        raise ValueError("Input must be a 2x2 matrix.")

    a, b = matrix[0]
    c, d = matrix[1]

    # Calculate the determinant
    determinant = a * d - b * c

    if determinant == 0:
        raise ValueError("This matrix is singular and does not have an inverse.")

    # Calculate the inverse using the formula
    inverse_matrix = [
        [d / determinant, -b / determinant],
        [-c / determinant, a / determinant]
    ]
    
    return np.round(inverse_matrix,decimals=4)


def compute_covariance_matrix(semi_major_axis, semi_minor_axis, theta):
    """Calculate the covariance matrix for the given parameters."""
    D = compute_diagonal_matrix(semi_major_axis, semi_minor_axis)
    V = compute_rotation_matrix(theta)
    V_inv = inverse_2x2_matrix(V)
    covariance_matrix = V @ D @ V_inv
    return np.round(covariance_matrix,decimals=4)

def combined_covar(covariance_matrices):
    """Calculate the overall covariance matrix."""
    inv_covariances = [inverse_2x2_matrix(covar) for covar in covariance_matrices]
    sum_inv_covariances = sum(inv_covariances)
    resulting_covariance = inverse_2x2_matrix(sum_inv_covariances)
    return np.round(resulting_covariance, decimals=4)

def extract_tuples_to_coord_matrices(data):
    coordinates=[]
    for entry in (data):
        # Assuming each entry is in the format: (x, y), a, b, theta
        xy_tuple = entry[0]  # Extract the (x, y) tuple
        # Convert (x, y) tuple to a 2x1 matrix
        matrix = np.array([[xy_tuple[0]], [xy_tuple[1]]])  # Form [x; y]
        coordinates.append(matrix)
    return np.round(coordinates,decimals=4)

def extract_covar_matrices(data):
    covariance_matrices = []
    for (x, y), a, b, theta in data:
        covar_matrix = compute_covariance_matrix(a, b, theta)
        covariance_matrices.append(covar_matrix)
    return np.round(covariance_matrices,decimals=4)

def final_target_coord(data):
    covars = extract_covar_matrices(data)
    inv_covars = [inverse_2x2_matrix(covar) for covar in covars]
    coord_mat = extract_tuples_to_coord_matrices(data)
    sum_of_product_of_coord_invcovars=np.zeros((2,1))
    for coord, inv_covar in zip(coord_mat,inv_covars):
        product = inv_covar @ coord
        sum_of_product_of_coord_invcovars+=product
    return np.round(combined_covar(covars) @ sum_of_product_of_coord_invcovars,decimals=4)

def combine_ellipses(data):
    final_covar = combined_covar(extract_covar_matrices(data))
    final_loc = final_target_coord(data)
    eigenvalues, eigenvectors = np.linalg.eig(final_covar)
    semi_maj_axis = np.round(np.sqrt(np.max(eigenvalues)*5.99),decimals=4)
    semi_min_axis = np.round(np.sqrt(np.min(eigenvalues)*5.99),decimals=4)
    maj_axis_vector = eigenvectors[:,np.argmax(eigenvalues)]
    ratio = maj_axis_vector[1]/maj_axis_vector[0]
    orientation = 90-np.round(np.degrees(np.arctan(ratio)),decimals=4)
    if maj_axis_vector[0] * maj_axis_vector[1] < 0:
        orientation = -orientation
    return [(final_loc[0,0],final_loc[1,0]),semi_maj_axis,semi_min_axis,orientation]
