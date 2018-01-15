#For more information about this, watch this video: https://www.youtube.com/watch?v=2hfoX51f6sg

import math
import os
from svg.path import * #Thank you for using complex numbers as points
from p5 import *
def save_frame(filename,char="#"): #Sorta make a copy of saveFrame() since p5 doesn't have one
    global num_frames
    try:
        num_frames
    except NameError:
        num_frames=1
    name,ext=os.path.splitext(filename)
    num_char=name.count(char)
    frame=str(num_frames)
    name=list(name)
    iter_char=0
    sub=1
    if len(frame)>=num_char:
        sub=0
    for i in range(len(name)):
        if name[i]==char:
            if iter_char<num_char-len(frame):
                name[i]="0"
            else:
                name[i]=frame[iter_char-len(frame)-sub]
            iter_char+=1
    name=''.join(name)
    filename=name+ext
    num_frames+=1
    pyglet.image.get_buffer_manager().get_color_buffer().save(filename)
def integrate(func,start,end,dx=0.01):
    i=start
    area=0
    while i<=end:
        area+=func(i)*dx
        i+=dx
    return area
def get_coeffs(p,start,end): #Get the Fourier coefficients along with their index with a Path object as p
    coeffs=[]
    i=start
    while i<=end:
        c=(1/(2*math.pi))*integrate(lambda x:p.point(x/(2*math.pi))*Epicycle.Cycle(-i)(x),0,2*math.pi)
        coeffs.append((i,c))
        i+=1
    return coeffs
class Epicycle: #I made this before I was drawing the circles, but I left it in to simplify the code a bit
    class Cycle:
        def __init__(self,speed,rad=1): #Note that rad can be a complex number
            self.rad=rad
            self.speed=speed
        def __call__(self,x):
            return self.rad*math.e**(1j*self.speed*x)
    def __init__(self,cyc): #cyc must be a list/tuple of lists and/or tuples that have the format of (speed,radius)
        self.cycles=[]
        for i in range(len(cyc)):
            if type(cyc[i])!=tuple and type(cyc[i])!=list:
                raise TypeError("Input must be a list or tuple of tuples and/or lists")
            f=cyc[i]
            self.cycles.append(Epicycle.Cycle(f[0],f[1]))
    def __call__(self,x):
        total=0
        for f in self.cycles:
            total+=f(x)
        return total
def path_from_file(filename): #Won't get whole .svg file, just the first path it sees
    with open(filename) as f:
        shape=f.read()
    shape=shape.split("<g")[1].split("<path")[1].split(' d="')[1].split('"')[0]
    shape=parse_path(shape)
    return shape
def translate_path(p,trans): #Move all the points in a Path over by some complex number trans
    trans_p=Path()
    for s in p:
        if type(s)==Line:
            trans_p.append(Line(s.start+trans,s.end+trans))
        elif type(s)==CubicBezier:
            trans_p.append(CubicBezier(s.start+trans,s.control1+trans,s.control2+trans,s.end+trans))
        elif type(s)==QuadraticBezier:
            trans_p.append(QuadraticBezier(s.start+trans,s.control+trans,s.end+trans))
        elif type(s)==Arc:
            trans_p.append(Arc(s.start+trans,s.radius,s.rotation,s.arc,s.sweep,s.end+trans))
    trans_p.closed=p.closed
    return trans_p
if not os.path.exists("frames"): #If a "frames" folder doesn't exist, make it
    os.mkdir("frames")
shape=path_from_file("test.svg")
print("Getting average coordinate...")
avg_coord=integrate(lambda x:shape.point(x),0,1) #Use the fact that the average point of a function f on the interval [a,b] is (1/(b-a))*integral(f,a,b)
print("Done")
shape=translate_path(shape,-avg_coord) #Move all the points in shape so that the center is the average coordinate
print("Getting coefficients...")
coeffs=get_coeffs(shape,-50,50)
print("Done")
cycles=[(coeffs[x][0],coeffs[x][1]) for x in range(len(coeffs))] #Package the coefficients into an input for an Epicycle
cycles.sort(key=lambda x:1/abs(x[1])) #Sort the cycles from largest to smallest radius to look better
epi=Epicycle(cycles)
t=0
points=[]
def setup():
    size(600,600)
def draw():
    global t,points
    if t>2*math.pi: #Stop drawing once the interval is over
        return
    background(0)
    translate(width/2,height/2)
    before=0
    c=before
    for cyc in epi.cycles: #Basically do what Epicycle.__call__ does but draw ellipses for a cool visual
        stroke(255)
        no_fill()
        ellipse((c.real,c.imag),abs(cyc.rad*2),abs(cyc.rad*2))
        c=before+cyc(t)
        before=c
    points.append(c)
    stroke(255,0,128)
    for i in range(1,len(points)): #Draw lines between all the previous points; obviously takes longer the more time that has passed
        now=points[i]
        old=points[i-1]
        line((now.real,now.imag),(old.real,old.imag))
    t+=.01
    save_frame("frames/###.png") #Because I only half-implemented saveFrame(), the first two frames don't have anything in them
run()
