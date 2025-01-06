# Combining Error Ellipses

## Introduction
In the context of maritime dynamic targeting, each type of weapon system has different level of target location accuracy required for effective employment. In a resource limited environment, target data with desired accuracy may not always be available. However, there is a clever way, using Bayes' theorem and optimal weighting, to combine a set of relatively poor target location data and generate a new target data with higher fidelity, which may be the single factor that would determine whether a firing unit can engage a target or not.

This document presents a Python code that combines a set of error ellipses to generate an improved error ellipse with the greater accuracy of source location. This code can be used to produce a smaller circular error probability (CEP) required for a given weapon system from a set of larger CEPs. 

## Definitions
### Error Ellipse
An error ellipse represents the estimate location of a signal source. This ellipse is a contour line of a bivariate Gaussian distribution typically with 95% confidence level; there is a 95% chance that the source is located inside the ellipse.

### Circular Error Probability

CEP is the radius of a circle that contains the target with a certain confidence level. In this document, CEP is assumed to has a confidence level of 95% or higher. A given error ellipse can easily converted into CEP by simply considering the semi-major axis of an error ellipse as the CEP.

<p align="center">
<img width="371" alt="CEP" src="https://github.com/user-attachments/assets/56aac738-5982-4c6d-a1cb-a57a76418a88" />
</p>

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
$$

where $v_{a}=\begin{bmatrix} v_{ax} \\ v_{ay} \end{bmatrix}$ and $v_{b}=\begin{bmatrix} v_{bx} \\ v_{by} \end{bmatrix}$ represent normalized vectors in the direction of major axis and minor axis, respectively, and $\sqrt{λ_{a}*χ^2}$ and $\sqrt{λ_{b}*χ^2}$ represent lengths of semi-major axis and semi-minor axis, respectively. $χ^2$ is the chi-squared value with two degrees of freedom. For an error ellipse with 95% confidence level, $χ^2=5.99.$ We can determine V and D from input data and hence determine covariance matrix as follows:
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
<p align="center">
<img width="848" alt="Data_conversion" src="https://github.com/user-attachments/assets/019f7aa8-1fcb-42b5-980a-b16d0dc4df5d" />
</p>
Note 90-𝜃 comes from the fact that true heading is measured from y-axis in a clockwise direction while typical x-y coordinate angle is measured from x-axis in counterclockwise direction.

## Combine Ellipses
Using the converted data, error ellipses can be combined to produce a new ellipse. The resulting ellipse center and covariance matrix can be found using two equations
$$𝜇_{f}=C_{f}\sum_{i}C_{i}^{-1}$$
$$C_{f}=(\sum_{i}(C_{i})^{-1})^{-1},$$
where $𝜇_{i}$ are error ellipse centers and $C_{i}$ are covariance matrices from the converted input data. See [1] and [2] for detailed derivation of these equations. The resulting ellipse center is the improved estimate of the target location relative to ellipse 1. This relative location can be converted into MGRS. The resulting covariance matrix can be decomposed into eigenvectors and eigenvalues, which will provide semi-major axis length, semi-minor length, and the orientation of the ellipse.

<p align="center">
<img width="594" alt="Final" src="https://github.com/user-attachments/assets/c4d1719c-2c15-450c-8089-f844603ddcf9" />
</p>

Below is the resulting plot with the example input ellipse data presented previously. Note the combined ellipse has significantly smaller CEP than that of input error ellipses. 

<p align="center">
<img width="496" alt="Combined_Ellipse" src="https://github.com/user-attachments/assets/2e5dbe3c-e01c-4d03-8d3a-b23c59875250" />
</p>

Users must also note that this algorithm assumes that the error ellipses are collected at the same time. In practice, the time of collection will be different for each error ellipse, in which case lengths of axes must be reestimated based on the speed at which the target was moving and the distance it traveled from the time of collection until some common reference time for all error ellipses. 

## References

<a id="Martello"></a>
[1] Davis, John E. "Combining Error Ellipses." CXC memo (2007).     
[2] Orechovesky Jr, Joseph R. "Single source error ellipse combination." Master's thesis, Naval Postgraduate School, Monterey, CA (1996).   
[3] Erten, Oktay, and Clayton V. Deutsch. "Combination of multivariate Gaussian distributions through error ellipses." Geostafisfics Lessons (2020).    
[4] Blachman, Nelson M. "On combining target-location ellipses." IEEE Transactions on Aerospace and Electronic Systems 25.2 (1989): 284-287.
