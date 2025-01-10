from flask import Flask, render_template, request, jsonify
import matplotlib.pyplot as plt
import io
import base64
import ast
import numpy as np
import combine_ellipses as ce
import convert_coordinates as cc
import plot_ellipses as pe
import copy

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    output_data = None
    plot_url = None
    input_data= [['51RVG9297470182', 3.7757, 0.56, 29.16], ['51RVG9116274139', 1.73, 0.86, 123]]
    if request.method == 'POST':
        input_data= request.form['input_data']
        
        # Get the input data from the form
        try:
            data = ast.literal_eval(request.form['input_data'])
            if not isinstance(data, list):
                raise ValueError("Input must be a list.")
                
            for sublist in data:
                if not (isinstance(sublist, list) and len(sublist) == 4):
                    raise ValueError("Each sublist must contain exactly 4 elements.")
                if not isinstance(sublist[0], str) or not all(isinstance(x, (int, float)) for x in sublist[1:]):
                    raise ValueError("The first element must be a string and the last three must be floats.")
            
            
            output_data=copy.deepcopy(data)
    
            # step 1: convert MGRS grids into relative (x,y) coordinates in NM.
            converted_input_data=cc.convert_input_data(data)
            
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
                
            # Save plot to a string in base64 format
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            plt.close()
            output_data= output_data[-1]
            
            response = {'output': output_data, 'plot_url': plot_url}
            return jsonify(response)
        except Exception as e:
            return jsonify({'output': f"Error Processing Input: {e}", 'plot_url': None})
    return render_template('readme.html', input_data=input_data)

if __name__ == '__main__':
    app.run(debug=True)
