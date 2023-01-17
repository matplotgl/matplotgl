# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

from matplotlib import colors as mplc
import numpy as np
import pythreejs as p3


class Points:

    def __init__(self, x, y, color='C0', s=3, zorder=0) -> None:

        self._x = np.asarray(x)
        self._y = np.asarray(y)
        self._zorder = zorder
        self._color = mplc.to_hex(color)
        self._geometry = p3.BufferGeometry(
            attributes={
                'position':
                p3.BufferAttribute(array=np.array(
                    [self._x, self._y,
                     np.full_like(self._x, self._zorder - 50)],
                    dtype='float32').T),
            })
        self._material = p3.PointsMaterial(color=self._color, size=s)
        self._points = p3.Points(geometry=self._geometry, material=self._material)

    def get_bbox(self):
        pad = 0.03
        xmin = self._x.min()
        xmax = self._x.max()
        padx = pad * (xmax - xmin)
        ymin = self._y.min()
        ymax = self._y.max()
        pady = pad * (ymax - ymin)
        return {
            'left': xmin - padx,
            'right': xmax + padx,
            'bottom': ymin - pady,
            'top': ymax + pady
        }

    def _update(self):
        self._geometry.attributes['position'].array = np.array(
            [self._x, self._y,
             np.full_like(self._x, self._zorder - 50)],
            dtype='float32').T

    def get(self):
        return self._points

    def set_xdata(self, x):
        self._x = np.asarray(x)
        self._update()

    def set_ydata(self, y):
        self._y = np.asarray(y)
        self._update()

    def set_data(self, xy):
        self._x = np.asarray(xy[:, 0])
        self._y = np.asarray(xy[:, 1])
        self._update()
