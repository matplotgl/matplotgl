from .line import Line


def plot(ax, x, y, **kwargs):
    line = Line(x, y, **kwargs)
    ax.get_figure().scene.add(line._line)
    return line
