# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

from .line import Line


def plot(ax, *args, **kwargs):
    line = Line(*args, **kwargs)
    ax.add_artist(line)
    ax.autoscale()
    return line
