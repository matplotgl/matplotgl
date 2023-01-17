# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

import numpy as np

from .figure import Figure
from .axes import Axes
from .widgets import VBar


def subplots(nrows=1, ncols=1, **kwargs):

    fig = Figure(**kwargs)
    axs = [[Axes() for i in range(nrows)] for j in range(ncols)]
    for col in axs:
        for ax in col:
            fig.axes.append(ax)
            ax.set_figure(fig, width=fig.width / ncols, height=fig.height / nrows)
        fig.add(VBar(col))

    if nrows + ncols == 2:
        out = axs[0][0]
    elif ncols == 1:
        out = np.array(axs[0])
    elif nrows == 1:
        out = np.array([ax[0] for ax in axs])
    else:
        out = np.array(axs)
    return fig, out
