################################################################################
#################################IMANIPOURMEYSAM################################
##   In this code we have 4 functions, first one will return a list of lines  ##
##   of the given triangle, the second will check if there lines of triangle  ## 
##   have interaction with the given height, the third one will find the x,y  ##
##   coordinate of the line with the given height if there is an interaction  ##
##   and finally the 4th function use the 3 first functions to return a list  ##
##   like the list asked in the pdf guide.                                    ##
################################################################################
################################################################################

import stltools
import numpy as np

#convert a triangle into 3 lines and returning an array of 3 lines(first function).
def triangle2lines(triangle):
    p0 = triangle[0]
    p1 = triangle[1]
    p2 = triangle[2]
    line_1 = np.array([p0,p1])
    line_2 = np.array([p0,p2])
    line_3 = np.array([p1,p2])
    line_list = np.array([line_1,line_2,line_3])
    return line_list

#check if there is interaction with the line in the given z(second function).
def have_interaction(z,line):
    if line[0][2] < line[1][2]: 
        z_min = line[0][2]
        z_max = line[1][2]
    else:
        z_min = line[1][2]
        z_max = line[0][2]

    if  z_min<z<z_max:
       return True
    else:
       return False
   
# return the x,y coordinate of the interaction point with the given height(third function).
def find_x_y(z,line):

    x0 = line[0][0] # point0,x
    x1 = line[1][0] # point1,x
    y0 = line[0][1] # point0,y
    y1 = line[1][1] # point1,y
    z0 = line[0][2] # point0,z
    z1 = line[1][2] # point1,z
    X0 = abs(x0)
    X1 = abs(x1)
    Y0 = abs(y0)
    Y1 = abs(y1)
    Z0 = abs(z0)
    Z1 = abs(z1)
    if z1*z0 > 0:
        if x1*x0 > 0:
            slope_x  = float(abs(Z1-Z0)/abs(X1-X0))
        if x1*x0 < 0:
            slope_x  = float(abs(Z1-Z0)/abs(X0+X1))
        if y1*y0 > 0:
            slope_y  = float(abs(Z1-Z0)/abs(Y1-Y0))
        if y1*y0 < 0:
            slope_y  = float(abs(Z1-Z0)/abs(Y1+Y0))

    elif z1*z0 < 0:
        if x1*x0 > 0:
            slope_x  = float(abs(Z1+Z0)/abs(X1-X0))
        if x1*x0 < 0:
            slope_x  = float(abs(Z1+Z0)/abs(X1+X0))
        if y1*y0 > 0:
            slope_y  = float(abs(Z1+Z0)/abs(Y1-Y0))
        if y1*y0 < 0:
            slope_y  = float(abs(Z1+Z0)/abs(Y1+Y0))

    if z1 < z0:
        if x1 > x0:
            slope_x = -1 * slope_x
        if y1 > y0:
            slope_y = -1 * slope_y
    elif z0 < z1:
        if x1 < x0:
            slope_x = -1 * slope_x
        if y1 < y0: 
            slope_y = -1 * slope_y

    intercept_x = z1 - (slope_x * x1)
    intercept_y = z1 - (slope_y * y1)
    x = (z - intercept_x) / slope_x
    y = (z - intercept_y) / slope_y
    return np.array([x,y,z])

# use three previous functions to return an array like the list in the pdf guide(4th function)
def get_z_slice(triangle_list, z):
    all_points = np.array([])
    for triangle in triangle_list:
        tri_3lines = triangle2lines(triangle)#makeing the three lines of each triangle.
        coordinates_xy = np.array([])
        for cnt in range(3):#iterating in each line.(line 0, line 1 and line 2)
            if (have_interaction(z,tri_3lines[cnt])):# check if there is interaction with the line.
                    coordinates_xy = np.append(coordinates_xy,find_x_y(z,tri_3lines[cnt]),axis = 0)
    
        all_points = np.append(all_points,coordinates_xy)

    all_points = all_points.reshape((int(all_points.size/6),2,3))
    return all_points 

# get the list of triangle and convert the list into numpy object.(I am more comfortable with numpy) 
triangle_list = stltools.loadStlFile("bunny.stl")
triangle_list = np.asarray(triangle_list)



zlines = get_z_slice(triangle_list,0)
mylines = zlines.tolist()

#print the result the way asked in the pdf guide.
stltools.display(triangle_list,mylines)
