import numpy as np
import combine_ellipses as ce
import convert_coordinates as cc
import plot_ellipses as pe
import copy

input_data = [
    # [MGRS, semi-maj axis in NM, semi-minor axis in NM, 
    # 0 < orientaion of major axis in degrees of true heading < 180]
    ['51RVG9297470182', 3.7757, 0.56, 29.16],  
    ['51RVG9116274139', 1.73, 0.86, 123]
]

output_data=copy.deepcopy(input_data)

# step 1: convert MGRS grids into relative (x,y) coordinates in NM.
converted_input_data=cc.convert_input_data(input_data)

# step 2: combine ellipses
## (x,y), semi-maj, semi-min, and orientation of the combined ellipse
combined_ellipse = ce.combine_ellipses(converted_input_data)

## append the combined ellipse to the data to be plotted
converted_input_data.append(combined_ellipse)

## append the combined ellipse to the output data for grid conversion
output_data.append(copy.deepcopy(combined_ellipse))

## calculate the combined ellipse center location in MGRS based on relative distance
combined_mgrs=cc.calculate_new_mgrs(output_data[0][0],combined_ellipse[0])
output_data[-1][0]=combined_mgrs
print(f"""Combined Ellipse Center is {output_data[-1][0]}
Circular Error Probability Radius is {np.round(output_data[-1][1]*6076.12,decimals=4)} ft""")

# step 3: plot ellipses
pe.plot_ellipses(converted_input_data,output_data[-1][0],np.round(output_data[-1][1]*6076.12,decimals=4))