# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

from .points import Points


def scatter(ax, x, y, **kwargs):
    pts = Points(x=x, y=y, **kwargs)
    ax.add_artist(pts)
    ax.autoscale()
    return pts
