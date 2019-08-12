from numpy import sqrt, linspace
from numpy.random import uniform

from bokeh.plotting import figure
from bokeh.io import show

SIZE = 1000

xs = linspace(0, 1, 1000)
ys = sqrt(1 - xs ** 2)

pts = uniform(0, 1, size=(SIZE, 2))
inside = pts[:, 0] ** 2 + pts[:, 1] ** 2 < 1

fig = figure()
fig.line(xs, ys, color='black')
fig.scatter(pts[inside][:, 0], pts[inside][:, 1], color='blue')
fig.scatter(pts[~inside][:, 0], pts[~inside][:, 1], color='red')
show(fig)
