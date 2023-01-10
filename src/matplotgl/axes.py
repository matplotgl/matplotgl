# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

from .spine import Spine
from .transform import Transform
from .utils import value_to_string
from .widgets import Box, HBar, VBar

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
        # self._transformx = Transform()
        # self._transformy = Transform()
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
            color=self.background_color,
            # color='red',
            side='DoubleSide')
        self._background_mesh = p3.Mesh(geometry=self._background_geometry,
                                        material=self._background_material,
                                        position=(0, 0, -200))

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
        self._zoom_rect_line = p3.Line(geometry=self._zoom_rect_geometry,
                                       material=p3.LineBasicMaterial(
                                           color='black', linewidth=1),
                                       visible=False)

        # xticklabels = self._make_xticks()
        # yticklabels = self._make_yticks()
        # self._left_spine = Spine(kind='left', transform=self._transformy)
        # self._right_spine = Spine(kind='right',
        #                           transform=self._transformy,
        #                           ticks=False)
        # self._bottom_spine = Spine(kind='bottom', transform=self._transformx)
        # self._top_spine = Spine(kind='top',
        #                         transform=self._transformx,
        #                         ticks=False)

        # self._outline = p3.Group([
        #     self._left_spine, self._right_spine, self._bottom_spine,
        #     self._top_spine
        # ])
        self._frame = _make_frame()

        # self.width = 600
        # self.height = 400
        # self.camera = p3.PerspectiveCamera(position=[0.0, 0, 2],
        #                                    aspect=self.width / self.height)
        # self.camera = p3.OrthographicCamera(-0.1, 1.1, 1.1, -0.1, -1, 100)
        self.camera = p3.OrthographicCamera(-0.001, 1.0, 1.0, -0.001, -1, 300)
        # self.scene = p3.Scene(children=[
        #     self.camera, self._background_mesh, self._left_spine,
        #     self._right_spine, self._bottom_spine, self._top_spine,
        #     self._frame, self._zoom_rect_line
        # ],
        #                       background=self.background_color)

        self.scene = p3.Scene(children=[
            self.camera, self._background_mesh, self._zoom_rect_line
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
            layout={'border': 'solid 2px'})

        self._zoom_mouse_down = False
        self._zoom_mouse_moved = False
        self._zoom_xmin = None
        self._zoom_xmax = None
        self._zoom_ymin = None
        self._zoom_ymax = None

        # self._left_bar = ipw.HTML(yticklabels,
        #                           layout={'height': f'{self._height}px'})
        self._left_bar = ipw.HTML(self._make_yticks())
        self._right_bar = ipw.HTML()
        self._bottom_bar = ipw.HTML(self._make_xticks())
        # self._bottom_bar = ipw.Button(icon='home', layout={'width': '600px'})
        self._top_bar = ipw.HTML()
        # # self._frame = _make_frame()

        # # limits = [[self.xmin, self.xmax], [self.ymin, self.ymax], [0, 0]]
        # # self.ticks = self._make_ticks(limits=limits)

        super().__init__([
            self._left_bar,
            VBar([self._top_bar, self.renderer]), self._right_bar
        ])
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
                # self.zoom({
                #     'left': array[:, 0].min(),
                #     'right': array[:, 0].max(),
                #     'bottom': array[:, 1].min(),
                #     'top': array[:, 1].max()
                # })
                self.zoom([
                    array[:, 0].min(), array[:, 0].max(), array[:, 1].min(),
                    array[:, 1].max()
                ])
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

    def scatter(self, *args, **kwargs):
        from .scatter import scatter as s
        return s(self, *args, **kwargs)

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
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

        # self._transformx.update(low=xmin, high=xmax)
        # self._transformy.update(low=ymin, high=ymax)
        # self._apply_zoom()
        self._background_mesh.geometry = p3.BoxGeometry(
            width=1.1 * (self.xmax - self.xmin),
            height=1.1 * (self.ymax - self.ymin),
            widthSegments=1,
            heightSegments=1)
        # self._background_geometry.width = 1.1 * (xmax - xmin)
        # self._background_geometry.height = 1.1 * (ymax - ymin)
        self._background_mesh.position = [
            0.5 * (self.xmin + self.xmax), 0.5 * (self.ymin + self.ymax),
            self._background_mesh.position[-1]
        ]
        # self.camera.left = self.xmin
        # self.camera.right = self.xmax
        # self.camera.bottom = self.ymin
        # self.camera.top = self.ymax
        self.reset()

    def add_artist(self, artist):
        self._artists.append(artist)
        self.scene.add(artist.get())

    def get_figure(self):
        return self._fig

    def _make_xticks(self, left, right) -> str:
        """
        Create tick labels on outline edges
        """
        ticker_ = ticker.AutoLocator()
        ticks = ticker_.tick_values(left, right)
        string = '<div style=\"position: relative;\">'
        for tick in ticks:
            if left <= tick <= right:
                x = tick * self.width - 5
                string += (
                    f'<div style=\"position: absolute; left: {x}px;top: 0px;'
                    f'text-align: center;display:inline-block;\">{value_to_string(tick)}</div>'
                )
                string += f'<div style=\"position: absolute; left: {x}px;top: -8px\">&#9589;</div>'
        string += '</div>'
        return string

    def _make_yticks(self, bottom, top) -> str:
        """
        Create tick labels on outline edges
        """
        ticker_ = ticker.AutoLocator()
        ticks = ticker_.tick_values(bottom, top)
        string = '<div style=\"position: relative;\">'
        for tick in ticks:
            if bottom <= tick <= top:
                y = self.height - (tick * self.height) - 18
                string += f'<div style=\"position: absolute; top: {y}px;\">{value_to_string(tick)}</div>'
        string += '</div>'
        return string

    def zoom(self, box):
        self._zoom_xmin = box[0]
        self._zoom_xmax = box[1]
        self._zoom_ymin = box[2]
        self._zoom_ymax = box[3]
        self.camera.left = self._zoom_xmin
        self.camera.right = self._zoom_xmax
        self.camera.bottom = self._zoom_ymin
        self.camera.top = self._zoom_ymax
        self._bottom_bar.value = self._make_xticks(left=self._zoom_xmin,
                                                   right=self._zoom_xmax)
        self._left_bar.value = self._make_yticks(bottom=self._zoom_ymin,
                                                 top=self._zoom_ymax)

    def _apply_zoom(self):
        for artist in self._artists:
            artist._apply_transform()

        # self._left_spine.set_transform(self._transformy)
        # self._right_spine.set_transform(self._transformy)
        # self._bottom_spine.set_transform(self._transformx)
        # self._top_spine.set_transform(self._transformx)
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
        # self._transformx.reset()
        # self._transformy.reset()
        # self._apply_zoom()
        # self.camera.left = -0.1
        # self.camera.right = 1.1
        # self.camera.top = 1.1
        # self.camera.bottom = -0.1

        self.camera.left = self.xmin
        self.camera.right = self.xmax
        self.camera.bottom = self.ymin
        self.camera.top = self.ymax
        self._bottom_bar.value = self._make_xticks(left=self.xmin,
                                                   right=self.xmax)
        self._left_bar.value = self._make_yticks(bottom=self.ymin,
                                                 top=self.ymax)

    def set_figure(self, fig):
        self._fig = fig
        # self._fig.camera.add(self._outline)
        self.width = self._fig.width
        self.height = self._fig.height
        # self._left_bar.layout = {'height': f'{self._height-2}px'}
        # self._fig.left_bar.children += (self._left_bar, )
        # self._fig.bottom_bar.children += (self._bottom_bar, )

        # self._frame.material.color = self._fig.background_color
