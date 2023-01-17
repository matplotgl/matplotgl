# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

from matplotlib import colors as mplc
import pythreejs as p3
import numpy as np


class Line:

    def __init__(self, x, y, fmt='-', color='C0', ls='solid', lw=1, ms=5, zorder=0):

        self._x = np.asarray(x)
        self._y = np.asarray(y)
        self._zorder = zorder
        self._geometry = p3.BufferGeometry(
            attributes={
                'position':
                p3.BufferAttribute(array=np.array(
                    [self._x, self._y,
                     np.full_like(self._x, self._zorder - 50)],
                    dtype='float32').T),
            })

        self._color = mplc.to_hex(color)
        self._line = None
        self._vertices = None
        if '-' in fmt:
            if ls == 'solid':
                self._line_material = p3.LineBasicMaterial(color=self._color,
                                                           linewidth=lw)
            elif ls == 'dashed':
                self._line_material = p3.LineDashedMaterial(color=self._color,
                                                            linewidth=lw)
            self._line = p3.Line(geometry=self._geometry, material=self._line_material)

        if 'o' in fmt:
            self._vertices_material = p3.PointsMaterial(color=self._color, size=ms)
            self._vertices = p3.Points(geometry=self._geometry,
                                       material=self._vertices_material)

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

    def get(self):
        out = []
        if self._line is not None:
            out.append(self._line)
        if self._vertices is not None:
            out.append(self._vertices)
        return p3.Group(children=out) if len(out) > 1 else out[0]
