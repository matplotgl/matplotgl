# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

from .transform import Transform
from .utils import value_to_string

import ipywidgets as ipw
import pythreejs as p3
from matplotlib import ticker
import numpy as np
from typing import List, Tuple

# def _make_sprite(string: str,
#                  position: Tuple[float, float, float],
#                  color: str = "black",
#                  size: float = 1.0) -> p3.Sprite:
#     """
#     Make a text-based sprite for axis tick.
#     """
#     sm = p3.SpriteMaterial(map=p3.TextTexture(string=string,
#                                               color=color,
#                                               size=300,
#                                               squareTexture=False),
#                            transparent=True)
#     return p3.Sprite(material=sm, position=position, scale=[size, size, size])


def _make_outline_array(xticks, yticks, tick_size=0.02):
    x = [0]
    for yt in yticks:
        x += [0, tick_size, 0]
    x += [0, 1, 1]
    for xt in xticks[::-1]:
        x += [xt, xt, xt]
    x += [0]

    y = [0]
    for yt in yticks:
        y += [yt, yt, yt]
    y += [1, 1, 0]
    for xt in xticks[::-1]:
        y += [0, tick_size, 0]
    y += [0]
    return np.array([x, y, np.zeros_like(x)], dtype='float32').T


def _make_outline(xticks, yticks, color='black', tick_size=0.02):
    array = _make_outline_array(xticks=xticks,
                                yticks=yticks,
                                tick_size=tick_size)
    geom = p3.BufferGeometry(attributes={
        'position': p3.BufferAttribute(array=array),
    })
    material = p3.LineBasicMaterial(color=color, linewidth=1)
    return p3.Line(geometry=geom, material=material)


# def _make_frame(color='white'):
#     dx = 1.0
#     x = np.array([-dx, -dx, 1 + dx, 1 + dx, 0, 0, 1, 1])
#     y = np.array([-dx, 1 + dx, 1 + dx, -dx, 0, 1, 1, 0])

#     vertices = np.array([x, y, np.zeros_like(x)], dtype='float32').T

#     faces = np.asarray(
#         [[0, 4, 1], [1, 4, 5], [1, 5, 2], [2, 5, 6], [2, 6, 3], [3, 6, 7],
#          [0, 3, 7], [0, 7, 4]],
#         dtype='uint16').ravel()  # We need to flatten index array

#     geom = p3.BufferGeometry(attributes=dict(
#         position=p3.BufferAttribute(vertices, normalized=False),
#         index=p3.BufferAttribute(faces, normalized=False),
#     ))

#     return p3.Mesh(geometry=geom,
#                    material=p3.MeshBasicMaterial(color=color),
#                    position=[0, 0, -1])


class Axes:

    def __init__(self) -> None:

        self.xmin = 0.0
        self.xmax = 1.0
        self.ymin = 0.0
        self.ymax = 1.0
        self._transformx = Transform()
        self._transformy = Transform()
        self._fig = None
        self._artists = []
        self._width = 100
        self._height = 100
        self.font_size = 14

        xticklabels, xticks = self._make_xticks(transform=self._transformx,
                                                width=self._width)
        yticklabels, yticks = self._make_yticks(transform=self._transformy,
                                                height=self._height)
        self._outline = _make_outline(xticks=xticks, yticks=yticks)

        self._left_bar = ipw.HTML(yticklabels)
        self._right_bar = ipw.HTML()
        self._bottom_bar = ipw.HTML(xticklabels)
        self._top_bar = ipw.HTML()
        # self._frame = _make_frame()

        # limits = [[self.xmin, self.xmax], [self.ymin, self.ymax], [0, 0]]
        # self.ticks = self._make_ticks(limits=limits)

        # super().__init__()
        # for obj in (self._outline, self.ticks, self._frame):
        #     self.add(obj)

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

    def _make_xticks(self, transform, width) -> str:
        """
        Create tick labels on outline edges
        """
        low = transform.low
        high = transform.high
        ticker_ = ticker.AutoLocator()
        ticks = ticker_.tick_values(low, high)
        string = f'<svg width=\"{width}\" height=\"{self.font_size}\">'
        values = []
        for tick in ticks:
            if low <= tick <= high:
                trans_pos = transform(tick)
                tick_pos = trans_pos * width
                string += (
                    f'<text fill=\"#000000\" font-size=\"{self.font_size}\" '
                    f'x=\"{tick_pos}\" y=\"{0.5*self.font_size}\"'
                    'dominant-baseline=\"middle\" text-anchor=\"middle\">'
                    f'{value_to_string(tick)}</text>')
                values.append(trans_pos)
        string += '</svg>'
        return string, values

    def _make_yticks(self, transform, height) -> str:
        """
        Create tick labels on outline edges
        """
        low = transform.low
        high = transform.high
        ticker_ = ticker.AutoLocator()
        ticks = ticker_.tick_values(low, high)
        string = f'<svg width=\"50px\" height=\"{height}\">'
        values = []
        for tick in ticks:
            if low <= tick <= high:
                trans_pos = transform(tick)
                tick_pos = height - (trans_pos * height)
                string += (
                    f'<text fill=\"#000000\" font-size=\"{self.font_size}\" '
                    f'x=\"20\" y=\"{tick_pos}\"'
                    'dominant-baseline=\"middle\" text-anchor=\"right\">'
                    f'{value_to_string(tick)}</text>')
                values.append(trans_pos)
        string += '</svg>'
        return string, values

    def zoom(self, box):
        self._transformx.zoom(low=self._transformx.inverse(box['left']),
                              high=self._transformx.inverse(box['right']))
        self._transformy.zoom(low=self._transformy.inverse(box['bottom']),
                              high=self._transformy.inverse(box['top']))
        self._apply_zoom()

    def _apply_zoom(self):
        for artist in self._artists:
            artist._apply_transform()
        # self.remove(self.ticks)
        # self.ticks = self._make_ticks(
        #     limits=[[self._transformx.low, self._transformx.high],
        #             [self._transformy.low, self._transformy.high], [0, 0]])
        # self.add(self.ticks)
        yticklabels, yticks = self._make_yticks(transform=self._transformy,
                                                height=self._height)
        self._left_bar.value = yticklabels
        xticklabels, xticks = self._make_xticks(transform=self._transformx,
                                                width=self._width)
        self._bottom_bar.value = xticklabels
        self._outline.geometry.attributes[
            'position'].array = _make_outline_array(xticks=xticks,
                                                    yticks=yticks,
                                                    tick_size=0.02)

    def reset(self):
        self._transformx.reset()
        self._transformy.reset()
        self._apply_zoom()

    def set_figure(self, fig):
        self._fig = fig
        self._fig.camera.add(self._outline)
        self._width = self._fig.width
        self._height = self._fig.height
        self._fig.left_bar.children += (self._left_bar, )
        self._fig.bottom_bar.children += (self._bottom_bar, )

        # self._frame.material.color = self._fig.background_color
