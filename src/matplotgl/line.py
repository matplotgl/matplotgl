# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

import pythreejs as p3
from matplotlib import ticker
import numpy as np
from typing import List, Tuple


class Line:

    def __init__(self, ax, x, y, color='blue') -> None:

        self._ax = ax
        self._x = x
        self._y = y
        self._geometry = p3.BufferGeometry(
            attributes={
                'position':
                p3.BufferAttribute(
                    array=np.array([self._x, self._y,
                                    np.zeros_like(self._x)],
                                   dtype='float32').T),
            })
        self._material = p3.LineBasicMaterial(color=color, linewidth=1)
        self._line = p3.Line(geometry=self._geometry, material=self._material)

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

    def _apply_transform(self):
        self._geometry.attributes['position'].array = np.array(
            [
                self._ax._transformx(self._x),
                self._ax._transformy(self._y),
                np.zeros_like(self._x)
            ],
            dtype='float32').T
