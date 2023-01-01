# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

import pythreejs as p3
from matplotlib import ticker
import numpy as np
from typing import List, Tuple


class Line:

    def __init__(self, x, y, color='blue') -> None:

        self._geometry = p3.BufferGeometry(
            attributes={
                'position':
                p3.BufferAttribute(
                    array=np.array([x, y, np.zeros_like(x)]).T),
            })
        self._material = p3.LineBasicMaterial(color=color, linewidth=1)
        self._line = p3.Line(geometry=self._geometry, material=self._material)
