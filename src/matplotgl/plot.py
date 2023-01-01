from .line import Line


def plot(ax, x, y, **kwargs):
    line = Line(x, y, **kwargs)
    ax.add(line._line)
