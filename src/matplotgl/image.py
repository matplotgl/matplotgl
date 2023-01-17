# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

import pythreejs as p3
import matplotlib as mpl
import numpy as np


class Image:

    def __init__(self, array, extent=None, cmap='viridis', zorder=0):

        self._array = np.asarray(array)
        self._extent = extent if extent is not None else [
            0, array.shape[1], 0, array.shape[0]
        ]
        self._zorder = zorder
        self._cmap = mpl.colormaps[cmap]
        self._texture = p3.DataTexture(
            data=self._cmap(self._array)[..., :3].astype('float32'),
            format="RGBFormat",
            type="FloatType",
        )

        self._geometry = p3.PlaneGeometry(width=self._extent[1] - self._extent[0],
                                          height=self._extent[3] - self._extent[2],
                                          widthSegments=1,
                                          heightSegments=1)

        self._image = p3.Mesh(geometry=self._geometry,
                              material=p3.MeshBasicMaterial(map=self._texture),
                              position=[
                                  0.5 * (self._extent[0] + self._extent[1]),
                                  0.5 * (self._extent[2] + self._extent[3]),
                                  self._zorder - 50
                              ])

    def get_bbox(self):
        return {
            'left': self._extent[0],
            'right': self._extent[1],
            'bottom': self._extent[2],
            'top': self._extent[3]
        }

    def get(self):
        return self._image
