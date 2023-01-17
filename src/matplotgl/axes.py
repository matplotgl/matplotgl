# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

import ipywidgets as ipw
import pythreejs as p3
from matplotlib import ticker
import numpy as np

from .utils import value_to_string


class Axes(ipw.GridBox):

    def __init__(self) -> None:

        self.background_color = "#ffffff"
        self.xmin = 0.0
        self.xmax = 1.0
        self.ymin = 0.0
        self.ymax = 1.0
        self._fig = None
        self._artists = []
        self._lines = []
        self._collections = []

        # Make background to enable box zoom
        self._background_geometry = p3.PlaneGeometry(width=2,
                                                     height=2,
                                                     widthSegments=1,
                                                     heightSegments=1)
        self._background_material = p3.MeshBasicMaterial(color=self.background_color,
                                                         #  side='DoubleSide'
                                                         )
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
                'position': p3.BufferAttribute(array=np.zeros((5, 3), dtype='float32')),
            })
        self._zoom_rect_line = p3.Line(geometry=self._zoom_rect_geometry,
                                       material=p3.LineBasicMaterial(color='black',
                                                                     linewidth=1),
                                       visible=False)

        self.camera = p3.OrthographicCamera(-0.001, 1.0, 1.0, -0.001, -1, 300)

        self.scene = p3.Scene(
            children=[self.camera, self._background_mesh, self._zoom_rect_line],
            background=self.background_color)

        self.controls = p3.OrbitControls(controlling=self.camera,
                                         enableZoom=False,
                                         enablePan=False)
        self.renderer = p3.Renderer(camera=self.camera,
                                    scene=self.scene,
                                    controls=[self.controls],
                                    width=200,
                                    height=200,
                                    layout={
                                        'border': 'solid 1px',
                                        'grid_area': 'renderer'
                                    })

        self._zoom_mouse_down = False
        self._zoom_mouse_moved = False
        self._zoom_xmin = None
        self._zoom_xmax = None
        self._zoom_ymin = None
        self._zoom_ymax = None

        self._leftspine = ipw.HTML(self._make_yticks(bottom=self.ymin, top=self.ymax),
                                   layout={'grid_area': 'leftspine'})
        self._rightspine = ipw.HTML(layout={'grid_area': 'rightspine'})
        self._bottomspine = ipw.HTML(self._make_xticks(left=self.xmin, right=self.xmax),
                                     layout={'grid_area': 'bottomspine'})
        self._topspine = ipw.HTML(layout={'grid_area': 'topspine', 'display': 'none'})
        self._title = ipw.HTML(layout={'grid_area': 'title'})
        self._xlabel = ipw.HTML(layout={'grid_area': 'xlabel'})
        self._ylabel = ipw.HTML(layout={'grid_area': 'ylabel'})

        super().__init__(children=[
            self._xlabel, self._ylabel, self._title, self._leftspine, self._rightspine,
            self._bottomspine, self._topspine, self.renderer
        ],
                         layout=ipw.Layout(
                             grid_template_columns=f'80px {self.width}px 50px',
                             grid_template_rows=f'35px {self.height}px 35px',
                             grid_template_areas='''
            ". topspine topspine"
            "leftspine renderer rightspine"
            "leftspine bottomspine bottomspine"
            '''))

    def on_mouse_down(self, change):
        self._zoom_mouse_down = True
        x, y, z = change['new']
        self._zoom_rect_line.geometry.attributes['position'].array = np.array(
            [[x, x, x, x, x], [y, y, y, y, y], [0, 0, 0, 0, 0]], dtype='float32').T
        self._zoom_rect_line.visible = True

    def on_mouse_up(self, *ignored):
        if self._zoom_mouse_down:
            self._zoom_mouse_down = False
            self._zoom_rect_line.visible = False
            if self._zoom_mouse_moved:
                array = self._zoom_rect_line.geometry.attributes['position'].array
                self.zoom([
                    array[:, 0].min(), array[:, 0].max(), array[:, 1].min(),
                    array[:, 1].max()
                ])
                self._zoom_mouse_moved = False

    def on_mouse_move(self, change):
        if self._zoom_mouse_down:
            self._zoom_mouse_moved = True
            x, y, z = change['new']
            new_pos = self._zoom_rect_line.geometry.attributes['position'].array.copy()
            new_pos[2:4, 0] = x
            new_pos[1:3, 1] = y
            self._zoom_rect_line.geometry.attributes['position'].array = new_pos

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

        self._background_mesh.geometry = p3.BoxGeometry(
            width=1.1 * (self.xmax - self.xmin),
            height=1.1 * (self.ymax - self.ymin),
            widthSegments=1,
            heightSegments=1)
        self._background_mesh.position = [
            0.5 * (self.xmin + self.xmax), 0.5 * (self.ymin + self.ymax),
            self._background_mesh.position[-1]
        ]
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
        string = '<div style=\"position: relative; height: 30px;\">'
        precision = max(-round(np.log10(right - left)) + 1, 0)
        for tick in ticks:
            if left + 0.01 * (right - left) <= tick <= right:
                x = (tick - left) / (right - left) * self.width - 5
                string += (f'<div style=\"position: absolute; left: {x}px; top: 4px;\">'
                           f'{value_to_string(tick, precision=precision)}</div>')
                string += (f'<div style=\"position: absolute; left: {x}px;top: -6px\">'
                           '&#9589;</div>')
        string += '</div>'
        return string

    def _make_yticks(self, bottom, top) -> str:
        """
        Create tick labels on outline edges
        """
        ticker_ = ticker.AutoLocator()
        ticks = ticker_.tick_values(bottom, top)
        string = ('<div style=\"position: relative;width: 80px;height: '
                  f'{self.height - 10}px;\">')
        precision = max(-round(np.log10(top - bottom)) + 1, 0)
        for tick in ticks:
            if bottom <= tick <= top - 0.01 * (top - bottom):
                y = self.height - ((tick - bottom) / (top - bottom) * self.height) - 15
                string += (
                    f'<div style=\"position: absolute; top: {y}px; right: 1px;\">'
                    f'{value_to_string(tick, precision=precision)} &#8211;</div>')
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
        self._bottomspine.value = self._make_xticks(left=self._zoom_xmin,
                                                    right=self._zoom_xmax)
        self._leftspine.value = self._make_yticks(bottom=self._zoom_ymin,
                                                  top=self._zoom_ymax)

    def _apply_zoom(self):
        for artist in self._artists:
            artist._apply_transform()

    def reset(self):
        self.camera.left = self.xmin
        self.camera.right = self.xmax
        self.camera.bottom = self.ymin
        self.camera.top = self.ymax
        self._bottomspine.value = self._make_xticks(left=self.xmin, right=self.xmax)
        self._leftspine.value = self._make_yticks(bottom=self.ymin, top=self.ymax)
        self._update_layout()

    def _update_layout(self):
        areas = ''
        columns = ''
        rows = ''
        if self._title.value:
            areas += (f'\"{"." if self._ylabel.value else ""} '
                      f'{"." if self._leftspine.value else ""} title .\"\n')
            rows += '30px '
        if self._topspine.value:
            areas += (f'\"{"." if self._ylabel.value else ""} '
                      f'{"." if self._leftspine.value else ""} '
                      'topspine topspine\"\n')
            rows += '35px '
        areas += (f'\"{"ylabel" if self._ylabel.value else ""} '
                  f'{"leftspine" if self._leftspine.value else ""} renderer '
                  f'{"rightspine" if self._rightspine.value else "."}\"\n')
        rows += f'{self.height}px '
        if self._bottomspine.value:
            areas += (f'\"{"." if self._ylabel.value else ""} '
                      f'{"leftspine" if self._leftspine.value else ""} '
                      'bottomspine bottomspine\"\n')
            rows += '35px '
        if self._xlabel.value:
            areas += (f'\"{"." if self._ylabel.value else ""} '
                      f'{"." if self._leftspine.value else ""} '
                      f'xlabel {"rightspine" if self._rightspine.value else "."}\"')
            rows += '30px'

        columns = (f'{"30px" if self._ylabel.value else ""} '
                   f'{"80px" if self._leftspine.value else ""} '
                   f'{self.width}px 35px')

        self.layout.grid_template_columns = columns
        self.layout.grid_template_rows = rows
        self.layout.grid_template_areas = areas

    def set_figure(self, fig):
        self._fig = fig
        self.width = self._fig.width
        self.height = self._fig.height
        self.renderer.layout.height = f'{self.height}px'
        self.renderer.layout.width = f'{self.width}px'

    def toggle_pan(self, value):
        self.controls.enablePan = value

    def set_xlabel(self, label, fontsize='1.3em'):
        if label:
            self._xlabel.value = (
                '<div style=\"position:relative; '
                f'width: {self.width}px; height: 30px;\">'
                '<div style=\"position:relative; top: 50%;left: 50%; '
                f'transform: translate(-50%, -50%); font-size: {fontsize};'
                f'float:left;\">{label.replace(" ", "&nbsp;")}</div></div>')
        else:
            self._xlabel.value = ''
        self._xlabel._raw_string = label
        self._update_layout()

    def get_xlabel(self):
        return self._xlabel._raw_string

    def set_ylabel(self, label, fontsize='1.3em'):
        if label:
            self._ylabel.value = (
                '<div style=\"position:relative; '
                f'width: 30px; height: {self.height}px;\">'
                '<div style=\"position:relative; top: 50%;left: 50%; '
                'transform: translate(-50%, -50%) rotate(-90deg); '
                f'font-size: {fontsize};'
                f'float:left;\">{label.replace(" ", "&nbsp;")}</div></div>')
        else:
            self._ylabel.value = ''
        self._ylabel._raw_string = label
        self._update_layout()

    def get_ylabel(self):
        return self._ylabel._raw_string

    def set_title(self, title, fontsize='1.3em'):
        if title:
            self._title.value = (
                '<div style=\"position:relative; '
                f'width: {self.width}px; height: 30px;\">'
                '<div style=\"position:relative; top: 50%;left: 50%; '
                f'transform: translate(-50%, -50%); font-size: {fontsize};'
                f'float:left;\">{title.replace(" ", "&nbsp;")}</div></div>')
        else:
            self._title.value = ''
        self._title._raw_string = title
        self._update_layout()

    def get_title(self):
        return self._title._raw_string

    def plot(self, *args, color=None, **kwargs):
        from .plot import plot as p
        if color is None:
            color = f'C{len(self._lines)}'
        line = p(self, *args, color=color, **kwargs)
        self._lines.append(line)
        return line

    def scatter(self, *args, color=None, **kwargs):
        from .scatter import scatter as s
        if color is None:
            color = f'C{len(self._collections)}'
        coll = s(self, *args, color=color, **kwargs)
        self._collections.append(coll)
        return coll

    def imshow(self, *args, **kwargs):
        from .imshow import imshow as im
        return im(self, *args, **kwargs)
