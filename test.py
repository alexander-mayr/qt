import numpy
import matplotlib.pyplot as plt    
n=200 #Grid size, 4 times my visualized output in order to be able to truncate some circles
empty_lattice=numpy.zeros((n,n)) #The empty 2D grid
radius=int(numpy.random.uniform(30,90)) #Radius
xc=int(numpy.random.uniform(0,n-radius)) #X center
yc=int(numpy.random.uniform(0,n-radius)) #Y center
x=0
y=radius
d=3-2*radius
while (x<=y):
    for hor in range(0,x): #This loop is my unfortunate attempt to fill the circle with 1s
        for ver in range(0,y):
            empty_lattice[xc+x][yc+y]=1 #1st octant
            empty_lattice[xc-x][yc+y]=1 #2nd octant
            empty_lattice[xc+x][yc-y]=1 #3rd octant
            empty_lattice[xc-x][yc-y]=1 #4th octant
            empty_lattice[xc+y][yc+x]=1 #5th octant
            empty_lattice[xc-y][yc+x]=1 #6th octant
            empty_lattice[xc+y][yc-x]=1 #7th octant
            empty_lattice[xc-y][yc-x]=1 #8th octant
    if (d<0):
        d=d+4*x+6
    else:
        d=d+4*(x-y)+10
        y=y-1
    x=x+1     