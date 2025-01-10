import numpy as np
import plotly.graph_objects as go
from scipy.stats import multivariate_normal, chi2

# Define the mean and covariance matrix
mean = [0, 0]
cov = [[1, 0.5], [0.5, 1]]  # Non-zero off-diagonal elements for asymmetry

# Create grid and multivariate normal
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)
pos = np.dstack((X, Y))

# Multivariate normal distribution
rv = multivariate_normal(mean, cov)
Z = rv.pdf(pos)

# Calculate the chi-squared value for 95% probability
probability_level = 0.95
chi2_val = chi2.ppf(probability_level, df=2)

# Eigenvalues and eigenvectors for the covariance matrix
eigvals, eigvecs = np.linalg.eigh(cov)

# Calculate the ellipse parameters
theta = np.linspace(0, 2 * np.pi, 100)
ellipse = np.array([np.cos(theta), np.sin(theta)])  # Parametric equation of a circle

# Scale the circle to the ellipse using the eigenvalues and eigenvectors
scale = np.sqrt(chi2_val)
ellipse_transformed = eigvecs @ np.diag(np.sqrt(eigvals)) @ ellipse * scale

# Create the surface plot
surface = go.Surface(x=X, y=Y, z=Z, colorscale='Viridis', opacity=0.7, name='Gaussian Surface', showscale=True)

# Create the ellipse plot
ellipse_trace = go.Scatter3d(
    x=ellipse_transformed[0, :] + mean[0],
    y=ellipse_transformed[1, :] + mean[1],
    z=rv.pdf(np.dstack((ellipse_transformed[0, :] + mean[0], ellipse_transformed[1, :] + mean[1]))),
    mode='lines',
    line=dict(color='red', width=3),
    name='Error Ellipse'  # Label for the legend
)

# Create the figure
fig = go.Figure(data=[surface, ellipse_trace])

# Update layout for better visualization and white background
fig.update_layout(
    scene=dict(
        xaxis_title='X axis',
        yaxis_title='Y axis',
        zaxis_title='Probability Density',
        xaxis=dict(backgroundcolor='white'),
        yaxis=dict(backgroundcolor='white'),
        zaxis=dict(backgroundcolor='white')
    ),
    paper_bgcolor='white',  # Background color outside the plot
    plot_bgcolor='white',   # Background color of the plot area
    legend=dict(
        x=0.8,  # Position the legend closer to the plot
        y=0.9,
        bgcolor='rgba(255, 255, 255, 0.5)',
        bordercolor='black',
        borderwidth=1
    ),
    showlegend=True  # Ensure the legend is always shown
)

# Instead of showing in browser, save as HTML
fig.write_html("static/bivariate_gaussian_3d.html")