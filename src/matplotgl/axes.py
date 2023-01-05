# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

from .transform import Transform
from .utils import value_to_string

import pythreejs as p3
from matplotlib import ticker
import numpy as np
from typing import List, Tuple


def _make_sprite(string: str,
                 position: Tuple[float, float, float],
                 color: str = "black",
                 size: float = 1.0) -> p3.Sprite:
    """
    Make a text-based sprite for axis tick.
    """
    sm = p3.SpriteMaterial(map=p3.TextTexture(string=string,
                                              color=color,
                                              size=300,
                                              squareTexture=False),
                           transparent=True)
    return p3.Sprite(material=sm, position=position, scale=[size, size, size])


def _make_outline(color='black'):
    geom = p3.BufferGeometry(
        attributes={
            'position':
            p3.BufferAttribute(array=np.array(
                [[0, 0, 1, 1, 0], [0, 1, 1, 0, 0], [0, 0, 0, 0, 0]],
                dtype='float32').T),
        })
    material = p3.LineBasicMaterial(color=color, linewidth=1)
    return p3.Line(geometry=geom, material=material)


def _make_frame(color='white'):
    dx = 1.0
    x = np.array([-dx, -dx, 1 + dx, 1 + dx, 0, 0, 1, 1])
    y = np.array([-dx, 1 + dx, 1 + dx, -dx, 0, 1, 1, 0])

    vertices = np.array([x, y, np.zeros_like(x)], dtype='float32').T

    faces = np.asarray(
        [[0, 4, 1], [1, 4, 5], [1, 5, 2], [2, 5, 6], [2, 6, 3], [3, 6, 7],
         [0, 3, 7], [0, 7, 4]],
        dtype='uint16').ravel()  # We need to flatten index array

    geom = p3.BufferGeometry(attributes=dict(
        position=p3.BufferAttribute(vertices, normalized=False),
        index=p3.BufferAttribute(faces, normalized=False),
    ))

    return p3.Mesh(geometry=geom,
                   material=p3.MeshBasicMaterial(color=color),
                   position=[0, 0, -1])


class Axes(p3.Group):

    def __init__(self) -> None:

        self.xmin = 0.0
        self.xmax = 1.0
        self.ymin = 0.0
        self.ymax = 1.0
        self._transformx = Transform()
        self._transformy = Transform()
        self._fig = None
        self._artists = []

        self._outline = _make_outline()
        self._frame = _make_frame()

        limits = [[self.xmin, self.xmax], [self.ymin, self.ymax], [0, 0]]
        self._tick_size = 0.05
        self.ticks = self._make_ticks(limits=limits)

        super().__init__()
        for obj in (self._outline, self.ticks, self._frame):
            self.add(obj)

    def plot(self, *args, **kwargs):
        from .plot import plot as p
        return p(self, *args, **kwargs)

    def autoscale(self):
        xmin = np.inf
        xmax = np.NINF
        ymin = np.inf
        ymax = np.NINF
        for artist in self._artists:
            lims = artist.get_bbox()
            xmin = min(lims['left'], xmin)
            xmax = max(lims['right'], xmax)
            ymin = min(lims['bottom'], ymin)
            ymax = max(lims['top'], ymax)

        self._transformx.update(low=xmin, high=xmax)
        self._transformy.update(low=ymin, high=ymax)
        self._apply_zoom()

    def add_artist(self, artist):
        self._artists.append(artist)
        self._fig.scene.add(artist._line)

    def get_figure(self):
        return self._fig

    def _make_ticks(self, limits, ndim=2) -> p3.Group:
        """
        Create tick labels on outline edges
        """
        ticks_group = p3.Group()
        iden = np.identity(3, dtype=np.float32)
        ticker_ = ticker.MaxNLocator(5)
        transforms = [self._transformx, self._transformy]
        for axis in range(ndim):
            ticks = ticker_.tick_values(limits[axis][0], limits[axis][1])
            for tick in ticks:
                if limits[axis][0] <= tick <= limits[axis][1]:
                    tick_pos = iden[axis] * transforms[axis](
                        tick) - 0.05 * iden[(axis + 1) % 2]
                    ticks_group.add(
                        _make_sprite(string=value_to_string(tick),
                                     position=tick_pos.tolist(),
                                     size=self._tick_size))
        return ticks_group

    def zoom(self, box):
        self._transformx.zoom(low=self._transformx.inverse(box['left']),
                              high=self._transformx.inverse(box['right']))
        self._transformy.zoom(low=self._transformy.inverse(box['bottom']),
                              high=self._transformy.inverse(box['top']))
        self._apply_zoom()

    def _apply_zoom(self):
        for artist in self._artists:
            artist._apply_transform()
        self.remove(self.ticks)
        self.ticks = self._make_ticks(
            limits=[[self._transformx.low, self._transformx.high],
                    [self._transformy.low, self._transformy.high], [0, 0]])
        self.add(self.ticks)

    def reset(self):
        self._transformx.reset()
        self._transformy.reset()
        self._apply_zoom()

    def set_figure(self, fig):
        self._fig = fig
        self._frame.material.color = self._fig.background_color
