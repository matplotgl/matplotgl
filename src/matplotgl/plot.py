# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

from .line import Line


def plot(ax, x, y, **kwargs):
    line = Line(x=x, y=y, **kwargs)
    ax.add_artist(line)
    ax.autoscale()
    return line
