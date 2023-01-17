from .figure import Figure
from .axes import Axes


def subplots():

    fig = Figure()
    ax = Axes()
    fig.add_axes(ax)
    return fig, ax
