# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

from .transform import Transform
from .utils import value_to_string
from .widgets import HBar

import ipywidgets as ipw
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


# def _make_outline_array(xticks, yticks, tick_size=0.02):
#     x = [0]
#     for yt in yticks:
#         x += [0, tick_size, 0]
#     x += [0, 1, 1]
#     for xt in xticks[::-1]:
#         x += [xt, xt, xt]
#     x += [0]

#     y = [0]
#     for yt in yticks:
#         y += [yt, yt, yt]
#     y += [1, 1, 0]
#     for xt in xticks[::-1]:
#         y += [0, tick_size, 0]
#     y += [0]
#     return np.array([x, y, np.zeros_like(x)], dtype='float32').T


def _make_outline(color='black'):
    # array = _make_outline_array(xticks=xticks,
    #                             yticks=yticks,
    #                             tick_size=tick_size)
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


class Axes(HBar):

    def __init__(self) -> None:

        self.background_color = "#f0f0f0"
        self.xmin = 0.0
        self.xmax = 1.0
        self.ymin = 0.0
        self.ymax = 1.0
        self._transformx = Transform()
        self._transformy = Transform()
        self._fig = None
        self._artists = []
        # self._width = 200
        # self._height = 200

        # Make background to enable box zoom
        self._background_geometry = p3.BoxGeometry(width=2,
                                                   height=2,
                                                   widthSegments=1,
                                                   heightSegments=1)
        self._background_material = p3.MeshBasicMaterial(
            color=self.background_color, side='DoubleSide')
        self._background_mesh = p3.Mesh(geometry=self._background_geometry,
                                        material=self._background_material,
                                        position=(0, 0, -100))

        self._zoom_down_picker = p3.Picker(controlling=self._background_mesh,
                                           event='mousedown')
        self._zoom_up_picker = p3.Picker(controlling=self._background_mesh,
                                         event='mouseup')
        self._zoom_move_picker = p3.Picker(controlling=self._background_mesh,
                                           event='mousemove')

        self._zoom_rect_geometry = p3.BufferGeometry(
            attributes={
                'position': p3.BufferAttribute(array=np.zeros((5, 3))),
            })
        self._zoom_rect_material = p3.LineBasicMaterial(color='black',
                                                        linewidth=1)
        self._zoom_rect_line = p3.Line(geometry=self._zoom_rect_geometry,
                                       material=self._zoom_rect_material,
                                       visible=False)

        # xticklabels = self._make_xticks(transform=self._transformx,
        #                                 width=self._width)
        # yticklabels = self._make_yticks(transform=self._transformy,
        #                                 height=self._height)
        self._outline = _make_outline()
        self._frame = _make_frame()

        # self.width = 600
        # self.height = 400
        # self.camera = p3.PerspectiveCamera(position=[0.0, 0, 2],
        #                                    aspect=self.width / self.height)
        self.camera = p3.OrthographicCamera(-0.1, 1.1, 1.1, -0.1, -1, 100)
        # self.camera = p3.OrthographicCamera(-0.001, 1.0, 1.0, -0.001, -1, 100)
        self.scene = p3.Scene(children=[
            self.camera, self._background_mesh, self._outline, self._frame,
            self._zoom_rect_line
        ],
                              background=self.background_color)
        self.controls = p3.OrbitControls(controlling=self.camera,
                                         enableZoom=False,
                                         enablePan=False)
        self.renderer = p3.Renderer(
            camera=self.camera,
            scene=self.scene,
            controls=[self.controls],
            width=200,
            height=200,
            # antialiasing=True
        )

        self._zoom_mouse_down = False
        self._zoom_mouse_moved = False

        # # self._left_bar = ipw.HTML(yticklabels,
        # #                           layout={'height': f'{self._height}px'})
        # self._left_bar = ipw.HTML(yticklabels)
        # self._right_bar = ipw.HTML()
        # self._bottom_bar = ipw.HTML(xticklabels)
        # # self._bottom_bar = ipw.Button(icon='home', layout={'width': '600px'})
        # self._top_bar = ipw.HTML()
        # # self._frame = _make_frame()

        # # limits = [[self.xmin, self.xmax], [self.ymin, self.ymax], [0, 0]]
        # # self.ticks = self._make_ticks(limits=limits)

        super().__init__([self.renderer])
        # for obj in (self._outline, self.ticks, self._frame):
        #     self.add(obj)

    def on_mouse_down(self, change):
        self._zoom_mouse_down = True
        x, y, z = change['new']
        self._zoom_rect_line.geometry.attributes['position'].array = np.array(
            [[x, x, x, x, x], [y, y, y, y, y], [0, 0, 0, 0, 0]]).T
        self._zoom_rect_line.visible = True
        # print(x, y, z, self._zoom_rect_line.visible, self.camera.near,
        #       self.camera.far)

    def on_mouse_up(self, *ignored):
        if self._zoom_mouse_down:
            self._zoom_mouse_down = False
            self._zoom_rect_line.visible = False
            if self._zoom_mouse_moved:
                array = self._zoom_rect_line.geometry.attributes[
                    'position'].array
                self.zoom({
                    'left': array[:, 0].min(),
                    'right': array[:, 0].max(),
                    'bottom': array[:, 1].min(),
                    'top': array[:, 1].max()
                })
                self._zoom_mouse_moved = False

    def on_mouse_move(self, change):
        if self._zoom_mouse_down:
            self._zoom_mouse_moved = True
            x, y, z = change['new']
            new_pos = self._zoom_rect_line.geometry.attributes[
                'position'].array.copy()
            new_pos[2:4, 0] = x
            new_pos[1:3, 1] = y
            self._zoom_rect_line.geometry.attributes[
                'position'].array = new_pos

    @property
    def width(self):
        return self.renderer.width

    @width.setter
    def width(self, w):
        self.renderer.width = w

    @property
    def height(self):
        return self.renderer.height

    @height.setter
    def height(self, h):
        self.renderer.height = h

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
        self.scene.add(artist._line)

    def get_figure(self):
        return self._fig

    def _make_xticks(self, transform, width, tick_size=5) -> str:
        """
        Create tick labels on outline edges
        """
        low = transform.low
        high = transform.high
        ticker_ = ticker.AutoLocator()
        ticks = ticker_.tick_values(low, high)
        # string = f'<svg width=\"{width}\" height=\"36\" >'
        # values = []

        string = '<div style=\"position: relative;\">'
        for tick in ticks:
            if low <= tick <= high:
                trans_pos = transform(tick)
                x = trans_pos * width - 5
                # string += (
                #     f'<text fill=\"#000000\" font-size=\"{self.font_size}\" '
                #     f'x=\"{x}\" y=\"{tick_size + 5}\"'
                #     'dominant-baseline=\"hanging\" text-anchor=\"middle\">'
                #     f'{value_to_string(tick)}</text>')
                # string += (
                #     f'<line x1=\"{x}\" y1=\"0\" x2=\"{x}\"'
                #     f'y2=\"{tick_size}\" style=\"stroke:rgb(0,0,0);stroke-width:1\" />'
                # )
                string += (
                    f'<div style=\"position: absolute; left: {x}px;top: 0px;'
                    f'text-align: center;display:inline-block;\">{value_to_string(tick)}</div>'
                )
                string += f'<div style=\"position: absolute; left: {x}px;top: -8px\">&#9589;</div>'

                # values.append(trans_pos)
        string += '</div>'
        return string

    def _make_yticks(self, transform, height, tick_size=5) -> str:
        """
        Create tick labels on outline edges
        """
        low = transform.low
        high = transform.high
        ticker_ = ticker.AutoLocator()
        ticks = ticker_.tick_values(low, high)
        # string = f'<svg width=\"40px\" height=\"{height - 10}\">'
        string = ''
        string = '<div style=\"position: relative;\">'
        # values = []
        x = 41
        for tick in ticks:
            if low <= tick <= high:
                trans_pos = transform(tick)
                y = height - (trans_pos * height) - 18
                # string += (
                #     f'<text fill=\"#000000\" font-size=\"{self.font_size}\" '
                #     f'x=\"{x - tick_size - 5}\" y=\"{y}\"'
                #     'dominant-baseline=\"middle\" text-anchor=\"end\">'
                #     f'{value_to_string(tick)}</text>')
                # string += (
                #     f'<line x1=\"{x}\" y1=\"{y}\" x2=\"{x-tick_size}\"'
                #     f'y2=\"{y}\" style=\"stroke:rgb(0,0,0);stroke-width:1\" />'
                # )
                string += f'<div style=\"position: absolute; top: {y}px;\">{value_to_string(tick)}</div>'
        string += '</div>'
        return string

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
        # print('_apply_zoom', self._height)
        # yticklabels = self._make_yticks(transform=self._transformy,
        #                                 height=self._height)
        # self._left_bar.value = yticklabels
        # xticklabels = self._make_xticks(transform=self._transformx,
        #                                 width=self._width)
        # self._bottom_bar.value = xticklabels
        # # self._outline.geometry.attributes[
        # #     'position'].array = _make_outline_array(xticks=xticks,
        # #                                             yticks=yticks,
        # #                                             tick_size=0.02)

    def reset(self):
        self._transformx.reset()
        self._transformy.reset()
        self._apply_zoom()

    def set_figure(self, fig):
        self._fig = fig
        # self._fig.camera.add(self._outline)
        self.width = self._fig.width
        self.height = self._fig.height
        # self._left_bar.layout = {'height': f'{self._height-2}px'}
        # self._fig.left_bar.children += (self._left_bar, )
        # self._fig.bottom_bar.children += (self._bottom_bar, )

        # self._frame.material.color = self._fig.background_color
