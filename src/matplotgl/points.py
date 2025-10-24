# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

import warnings
from matplotlib import colors as mplc
import numpy as np
import pythreejs as p3

from .utils import fix_empty_range, find_limits


class Points:
    def __init__(self, x, y, color="C0", s=3, zorder=0) -> None:
        self._x = np.asarray(x)
        self._y = np.asarray(y)
        self._rendered_x = self._x.copy()
        self._rendered_y = self._y.copy()
        self._xscale = "linear"
        self._yscale = "linear"
        self._zorder = zorder
        self._color = mplc.to_hex(color)
        self._geometry = p3.BufferGeometry(
            attributes={
                "position": p3.BufferAttribute(
                    array=np.array(
                        [self._x, self._y, np.full_like(self._x, self._zorder)],
                        dtype="float32",
                    ).T
                ),
            }
        )
        self._material = p3.PointsMaterial(color=self._color, size=s)
        self._points = p3.Points(geometry=self._geometry, material=self._material)

    def get_bbox(self):
        pad = 0.03
        left, right = fix_empty_range(find_limits(self._x, scale=self._xscale, pad=pad))
        bottom, top = fix_empty_range(find_limits(self._y, scale=self._yscale, pad=pad))
        # xmin = self._x.min()
        # xmax = self._x.max()
        # padx = pad * (xmax - xmin)
        # ymin = self._y.min()
        # ymax = self._y.max()
        # pady = pad * (ymax - ymin)
        return {"left": left, "right": right, "bottom": bottom, "top": top}

    def _update(self):
        with warnings.catch_warnings(category=RuntimeWarning, action="ignore"):
            xx = self._x if self._xscale == "linear" else np.log10(self._x)
            yy = self._y if self._yscale == "linear" else np.log10(self._y)
        self._geometry.attributes["position"].array = np.array(
            # [xx, yy, np.full_like(xx, self._zorder - 50)],
            [xx, yy, np.full_like(xx, self._zorder)],
            dtype="float32",
        ).T

    def get(self):
        return self._points

    def get_xdata(self) -> np.ndarray:
        return self._x

    def set_xdata(self, x):
        self._x = np.asarray(x)
        self._update()

    def get_ydata(self) -> np.ndarray:
        return self._y

    def set_ydata(self, y):
        self._y = np.asarray(y)
        self._update()

    def set_data(self, xy):
        self._x = np.asarray(xy[:, 0])
        self._y = np.asarray(xy[:, 1])
        self._update()

    def _set_xscale(self, scale):
        self._xscale = scale
        self._update()

    def _set_yscale(self, scale):
        self._yscale = scale
        self._update()
