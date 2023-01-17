# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

from .image import Image


def imshow(ax, array, **kwargs):
    image = Image(array, **kwargs)
    ax.add_artist(image)
    ax.autoscale()
    return image
