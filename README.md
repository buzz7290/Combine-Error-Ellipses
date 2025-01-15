# Combining Error Ellipses
<p>Website: <a href="https://buzz7290.pythonanywhere.com">https://buzz7290.pythonanywhere.com</a></p>

## Introduction
In the context of maritime dynamic targeting, each type of weapon system requires a certain level of target location accuracy for effective employment. In a resource-limited environment, target data with desired accuracy may not always be available. However, there is a clever way, using Bayes' theorem and optimal weighting, to combine a set of relatively poor target location data to generate a new target data with higher fidelity, which could be the single factor that determines whether a firing unit can engage a target or not.

## Error Ellipse
An error ellipse represents the estimate location of a signal source. This ellipse is a contour line of a bivariate Gaussian distribution typically with 95% confidence level; there is a 95% probability that the source is located inside the ellipse. Bivariate Gaussian probability density function is given by    

<p>
$$f(x,y)=
\frac{exp[-\frac{(\frac{x-𝜇_{x}}{ρ})^2-\frac{2ρ(x-𝜇_{x})(y-𝜇_{y})}{σ_{x}σ_{y}}+(\frac{y-𝜇_{y}}{ρ})^2}{2(1-ρ^2)}]}
{2πσ_{x}σ_{y}\sqrt{1-ρ^2}},
$$
</p>
where \(𝜇_{x}\) and $𝜇_{y}$ are the means of x and y, respectively, $σ_{x}$ and $σ_{y}$ are the standard deviations of x and y, respectively, and ρ is the correlation coefficient between x and y.    
<p align="center">
<img width="496" alt="Plot" src="https://github.com/user-attachments/assets/1085897d-a624-476f-bd18-5eb51b13300c" />
</p>
The degree of error ellipse accuracy is typically determined by the length of the semi-major axis; the smaller the semi-major axis, the more accurate the target location. When multiple ellipses are obtained from a single signal source, each ellipse cannot represent 95% probability of target location because the total probability cannot be greater than 1. Therefore, we need to update the overall probability density function based on new observations. This document presents the process of combining a set of error ellipses to generate an improved error ellipse with the greater accuracy of the source location, method of which is based on Bayes' theorem. 

## Input Data Conversion
An observation of a signal from the source is represented by an error ellipse which can be defined by four parameters: center location in MGRS, length of semi-major axis in nautical miles (NM), length of semi-minor axis in NM, and orientation as true heading of the semi-major axis in degrees. Input of this algorithm is a set of ellipses, each with these four parameters, and output is another ellipse with more accurate MGRS estimate and smaller length of semi-major axis.

```
# Example input error ellipse data
input_data = [
    # [MGRS, semi-maj axis in NM, semi-minor axis in NM, 
    # 0 < orientaion of major axis in degrees of true heading < 180]
    ['51RVG9297470182', 3.7757, 0.56, 29.16],  
    ['51RVG9116274139', 1.73, 0.86, 123]
]
```

In order to combine error ellipses, this input data must be converted into a format more conducive to further processing. First, MGRS is converted to (x,y) coordinates in nautical miles on a tangent plane, where the center of the first ellipse is taken as a reference point (0,0). Since the distance between centers of error ellipses are usually much smaller than the earth's radius, the lengths of axes are sufficiently preserved by the tangent plane projection. In other words, arc lenghts can be approximated as straight lines on a 2D plane. Second, semi-major axis, semi-minor axis, and orientation of each ellipse are converted to a covariance matrix

$$C=\begin{bmatrix}
σ_{x}^2 & σ_{xy} \\
σ_{xy} & σ_{y}^2
\end{bmatrix},$$  

where $σ_{x}^2$ and $σ_{y}^2$ are variances of x and y, respectively, and $σ_{xy}$ is the covariance of x and y. Through spectral decomposition, the covariance matrix can be expressed as
$$C = VDV^{-1}=
\begin{bmatrix}
v_{ax} & v_{bx} \\
v_{ay} & v_{by}
\end{bmatrix}
\begin{bmatrix}
λ_{a} & 0 \\
0 & λ_{b}
\end{bmatrix}
\begin{bmatrix}
v_{ax} & v_{bx} \\
v_{ay} & v_{by}
\end{bmatrix}^{-1},$$

where $v_{a}=\begin{bmatrix} v_{ax} \\ v_{ay} \end{bmatrix}$ and $v_{b}=\begin{bmatrix} v_{bx} \\ v_{by} \end{bmatrix}$ represent normalized vectors in the direction of major axis and minor axis, respectively, and $\sqrt{λ_{a}*χ^2}$ and $\sqrt{λ_{b}*χ^2}$ represent lengths of semi-major axis and semi-minor axis, respectively. $χ^2$ is the chi-squared value with two degrees of freedom. For an error ellipse with 95% confidence level, $χ^2=5.99.$ We can determine V and D from input data as follows:
```
Let a = length of semi-major axis
    b = length of semi-minor axis
    𝜃 = true heading of semi-major axis
```
Then 
$$V=\begin{bmatrix} cos(90-𝜃) & -sin(90-𝜃) \\ sin(90-𝜃) & cos(90-𝜃) \end{bmatrix}$$
$$D=\begin{bmatrix}
a^2/χ^2 & 0 \\
0 & b^2/χ^2
\end{bmatrix}.$$

<p>From V and D, we can determine the covariance matrix C. This data conversion scheme is shown below.</p>

<p align="center">
<img width="848" alt="Data_conversion" src="https://github.com/user-attachments/assets/019f7aa8-1fcb-42b5-980a-b16d0dc4df5d" />
</p>
Note 90-𝜃 comes from the fact that true heading is measured from y-axis in a clockwise direction while typical x-y coordinate angle is measured from x-axis in counterclockwise direction.

## Combine Ellipses
Using the converted data, error ellipses can be combined to produce a new ellipse. The resulting ellipse center and covariance matrix can be found using two equations
$$𝜇_{f}=C_{f}\sum_{i}C_{i}^{-1}μ_{i}$$
$$C_{f}=(\sum_{i}(C_{i})^{-1})^{-1},$$
where $𝜇_{i}$ are error ellipse centers and $C_{i}$ are covariance matrices from the converted input data. See [1] and [2] for detailed derivation of these equations. The resulting ellipse center is the improved estimate of the target location relative to ellipse 1. This relative location can be converted into MGRS. The resulting covariance matrix can be decomposed into eigenvectors and eigenvalues, which will provide semi-major axis length, semi-minor length, and the orientation of the ellipse. This process is schematically shown below.

<p align="center">
<img width="594" alt="Final" src="https://github.com/user-attachments/assets/c4d1719c-2c15-450c-8089-f844603ddcf9" />
</p>

Input ellipses and the combined ellipse can be plotted for visual illustration of this combination process. Below is the resulting plot with the example input ellipse data presented previously. Note the combined ellipse has significantly smaller semi-major axis than those of input error ellipses.

<p align="center">
<img width="496" alt="Plot" src="https://github.com/user-attachments/assets/e5086df8-ac00-4c59-b189-29f113ac9e55" />
</p>

## Caveats
It is worth noting two caveats. First, users must be sufficiently confident that signals associated with error ellipses are emitted from the same source. Second, this algorithm assumes that the error ellipses are collected at the same time. In practice, the time of collection will be different for each error ellipse, in which case lengths of axes must be reestimated based on the speed at which the target was moving and the distance it traveled from the time of collection until some common reference time for all error ellipses.

## References
<a id="Martello"></a>
[1] Davis, John E. "Combining Error Ellipses." CXC memo (2007).     
[2] Orechovesky Jr, Joseph R. "Single source error ellipse combination." Master's thesis, Naval Postgraduate School, Monterey, CA (1996).   
[3] Erten, Oktay, and Clayton V. Deutsch. "Combination of multivariate Gaussian distributions through error ellipses." Geostafisfics Lessons (2020).    
[4] Blachman, Nelson M. "On combining target-location ellipses." IEEE Transactions on Aerospace and Electronic Systems 25.2 (1989): 284-287.    
[5] Florescu, Ionut. "Probability and stochastic processes." John Wiley & Sons, 2014.     
[6] California Institute of Technology Pasadena Jet Propulsion Laboratory. "Calculating the CEP (Circular Error Probable)." 1987.
