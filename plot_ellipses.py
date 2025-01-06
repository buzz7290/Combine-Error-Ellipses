import matplotlib.pyplot as plt
import numpy as np

def plot_ellipses(ellipses, center_f, CEP):
    """
    Plots multiple ellipses on the same figure.

    Parameters:
    ellipses: List of dictionaries where each dictionary contains:
        - 'center': tuple of (x_center, y_center)
        - 'semi_major_axis': length of semi-major axis
        - 'semi_minor_axis': length of semi-minor axis
        - 'orientation': angle of orientation in degrees
    """
    plt.figure(figsize=(8, 8))
    for i, ellipse in enumerate(ellipses):
        center = ellipse[0]
        semi_major_axis = ellipse[1]
        semi_minor_axis = ellipse[2]
        orientation = 90-ellipse[3]
        
        # Convert orientation angle from degrees to radians
        theta = np.deg2rad(orientation)

        # Parametric equation for ellipse
        t = np.linspace(0, 2 * np.pi, 100)
        x = semi_major_axis * np.cos(t)
        y = semi_minor_axis * np.sin(t)

        # Rotation matrix for orientation
        x_rot = x * np.cos(theta) - y * np.sin(theta)
        y_rot = x * np.sin(theta) + y * np.cos(theta)

        # Translate ellipse to center
        x_final = x_rot + center[0]
        y_final = y_rot + center[1]
        
        if i == len(ellipses)-1:
            plt.plot(x_final, y_final, color='green',label=f"Combined Ellipse" "\n" f"Center: {center_f}" "\n" f"CEP: {CEP} ft")
            plt.scatter(*center,color='green')
        # Plot each ellipse
        elif i<len(ellipses)-1:
            plt.plot(x_final, y_final,label=f"Ellipse {i+1}")
            plt.scatter(*center)
        
    plt.xlabel('Relative Longitude in NM')
    plt.ylabel('Relative Latitude in NM')
    plt.title('Combining Error Ellipses')
    plt.grid(True)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.legend()
    plt.axis('equal')
    plt.show()