# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

from contextlib import nullcontext
from ipycanvas import Canvas, hold_canvas
import ipywidgets as ipw
import pythreejs as p3
from matplotlib.axes import Axes as MplAxes
import numpy as np


from .line import Line
from .points import Points
from .image import Image


class Axes(ipw.GridBox):
    def __init__(self, *, ax: MplAxes, figure=None) -> None:
        self.background_color = "#ffffff"
        self._xmin = 0.0
        self._xmax = 1.0
        self._ymin = 0.0
        self._ymax = 1.0
        self._fig = None
        self._ax = ax
        self._artists = []
        self.lines = []
        self.collections = []

        # Make background to enable box zoom
        self._background_geometry = p3.PlaneGeometry(
            width=2, height=2, widthSegments=1, heightSegments=1
        )
        self._background_material = p3.MeshBasicMaterial(
            color=self.background_color,
            #  side='DoubleSide'
        )
        self._background_mesh = p3.Mesh(
            geometry=self._background_geometry,
            material=self._background_material,
            position=(0, 0, -200),
        )

        self._mouse_cursor_picker = p3.Picker(
            controlling=self._background_mesh, event="mousemove"
        )
        self._mouse_cursor_picker.observe(self._update_cursor_position, names=["point"])

        self._zoom_down_picker = p3.Picker(
            controlling=self._background_mesh, event="mousedown"
        )
        self._zoom_up_picker = p3.Picker(
            controlling=self._background_mesh, event="mouseup"
        )
        self._zoom_move_picker = p3.Picker(
            controlling=self._background_mesh, event="mousemove"
        )

        self._zoom_rect_geometry = p3.BufferGeometry(
            attributes={
                "position": p3.BufferAttribute(array=np.zeros((5, 3), dtype="float32")),
            }
        )
        self._zoom_rect_line = p3.Line(
            geometry=self._zoom_rect_geometry,
            material=p3.LineBasicMaterial(color="black", linewidth=1),
            visible=False,
        )

        self.camera = p3.OrthographicCamera(-0.001, 1.0, 1.0, -0.001, -1, 300)

        self.scene = p3.Scene(
            children=[self.camera, self._background_mesh, self._zoom_rect_line],
            background=self.background_color,
        )

        self.controls = p3.OrbitControls(
            controlling=self.camera, enableZoom=False, enablePan=False
        )
        self.renderer = p3.Renderer(
            camera=self.camera,
            scene=self.scene,
            controls=[self.controls, self._mouse_cursor_picker],
            width=200,
            height=200,
            layout={
                # "border": "solid 1px",
                "grid_area": "renderer",
                "padding": "0",
                "margin": "0",
            },
            antialias=True,
        )

        self._zoom_mouse_down = False
        self._zoom_mouse_moved = False
        self._zoom_xmin = None
        self._zoom_xmax = None
        self._zoom_ymin = None
        self._zoom_ymax = None

        params = {
            "xlabel": {"width": self.width, "height": 50},
            "ylabel": {"width": 50, "height": self.height},
            "title": {"width": self.width, "height": 50},
            "leftspine": {"width": 50, "height": self.height + 50},
            "rightspine": {"width": 50, "height": self.height},
            "bottomspine": {"width": self.width + 50, "height": 50},
            "topspine": {"width": self.width + 50, "height": 50},
        }

        self._canvases = {
            name: Canvas(
                width=param["width"],
                height=param["height"],
                layout={
                    "grid_area": name,
                    "padding": "0",
                    "margin": "0",
                },
            )
            for name, param in params.items()
        }

        # font_size = 12
        # for canvas in self._canvases.values():
        #     canvas.font = f"{font_size}px sans-serif"
        #     canvas.fill_style = "black"
        #     canvas.text_align = "center"

        # self._canvases["xlabel"].text_baseline = "top"
        # self._canvases["ylabel"].text_baseline = "middle"
        # self._canvases["title"].text_baseline = "bottom"
        # self._canvases["leftspine"].text_align = "right"
        # self._canvases["leftspine"].text_baseline = "middle"
        # self._canvases["rightspine"].text_align = "left"
        # self._canvases["rightspine"].text_baseline = "middle"
        # self._canvases["topspine"].text_align = "center"
        # self._canvases["topspine"].text_baseline = "bottom"
        # self._canvases["bottomspine"].text_align = "center"
        # self._canvases["bottomspine"].text_baseline = "bottom"

        if figure is not None:
            self.set_figure(figure)

        super().__init__(
            children=[
                *self._canvases.values(),
                self.renderer,
            ],
            layout=ipw.Layout(
                grid_template_columns="auto" * 4,
                grid_template_rows="auto" * 5,
                grid_template_areas="""
            ". . title ."
            ". . topspine topspine"
            "ylabel leftspine renderer rightspine"
            ". leftspine bottomspine bottomspine"
            ". . xlabel ."
            """,
                padding="0",
                grid_gap="0px 0px",
                margin="0",
            ),
        )

    def _update_cursor_position(self, change):
        # Add text at the bottom right corner of the topspine canvas
        x, y, z = change["new"]
        canvas = self._canvases["topspine"]
        with hold_canvas():
            canvas.clear()
            canvas.text_align = "right"
            canvas.fill_text(f"({x:.2f}, {y:.2f})", self.width - 10, canvas.height - 10)
            canvas.begin_path()
            canvas.move_to(0, canvas.height)
            canvas.line_to(self.width, canvas.height)
            canvas.stroke()

    def on_mouse_down(self, change):
        self._zoom_mouse_down = True
        x, y, z = change["new"]
        self._zoom_rect_line.geometry.attributes["position"].array = np.array(
            [[x, x, x, x, x], [y, y, y, y, y], [0, 0, 0, 0, 0]], dtype="float32"
        ).T
        self._zoom_rect_line.visible = True

    def on_mouse_up(self, *ignored):
        if self._zoom_mouse_down:
            self._zoom_mouse_down = False
            self._zoom_rect_line.visible = False
            if self._zoom_mouse_moved:
                array = self._zoom_rect_line.geometry.attributes["position"].array
                self.zoom(
                    [
                        array[:, 0].min(),
                        array[:, 0].max(),
                        array[:, 1].min(),
                        array[:, 1].max(),
                    ]
                )
                self._zoom_mouse_moved = False

    def on_mouse_move(self, change):
        # print("MOUSE MOVE", change)
        if self._zoom_mouse_down:
            self._zoom_mouse_moved = True
            x, y, z = change["new"]
            new_pos = self._zoom_rect_line.geometry.attributes["position"].array.copy()
            new_pos[2:4, 0] = x
            new_pos[1:3, 1] = y
            self._zoom_rect_line.geometry.attributes["position"].array = new_pos

    @property
    def width(self):
        return self.renderer.width

    @width.setter
    def width(self, w):
        self.renderer.width = w
        self._canvases["xlabel"].width = w
        self._canvases["title"].width = w
        self._canvases["bottomspine"].width = w + self._canvases["rightspine"].width
        self._canvases["topspine"].width = w + self._canvases["rightspine"].width

    @property
    def height(self):
        return self.renderer.height

    @height.setter
    def height(self, h):
        self.renderer.height = h
        self._canvases["ylabel"].height = h
        self._canvases["leftspine"].height = h + self._canvases["bottomspine"].height
        self._canvases["rightspine"].height = h

    def autoscale(self):
        xmin = np.inf
        xmax = -np.inf
        ymin = np.inf
        ymax = -np.inf
        for artist in self._artists:
            lims = artist.get_bbox()
            xmin = min(lims["left"], xmin)
            xmax = max(lims["right"], xmax)
            ymin = min(lims["bottom"], ymin)
            ymax = max(lims["top"], ymax)
        self._xmin = xmin
        self._xmax = xmax
        self._ymin = ymin
        self._ymax = ymax

        self._background_mesh.geometry = p3.BoxGeometry(
            width=2 * (self._xmax - self._xmin),
            height=2 * (self._ymax - self._ymin),
            widthSegments=1,
            heightSegments=1,
        )
        self._background_mesh.position = [
            0.5 * (self._xmin + self._xmax),
            0.5 * (self._ymin + self._ymax),
            self._background_mesh.position[-1],
        ]
        self.reset()

    def add_artist(self, artist):
        self._artists.append(artist)
        self.scene.add(artist.get())

    def get_figure(self):
        return self._fig

    def _make_xticks(self, hold=True):
        """
        Create tick labels on outline edges
        """
        # string = (
        #     '<div style="position: relative; height: 2em; background-color: red;">'
        #     '<svg height="2em" width="100%"><line x1="0" y1="0" x2="100%" y2="0" '
        #     'style="stroke:black;stroke-width:1" />'
        # )
        tick_length = 6
        label_offset = 3

        # # (xmin, xmax), (ymin, ymax) = self._ax.get_xlim(), self._ax.get_ylim()
        # xmin, xmax = self.camera.left, self.camera.right

        # xt = ax.get_xticks()

        xticks = self.get_xticks()
        xlabels = [lab.get_text() for lab in self.get_xticklabels()]

        xy = np.vstack((xticks, np.zeros_like(xticks))).T
        xticks_axes = self._ax.transAxes.inverted().transform(
            self._ax.transData.transform(xy)
        )[:, 0]

        print("MAKE X TICKS", xticks.min(), xticks.max())

        # print("textalign", self._canvases["bottomspine"].text_align)

        bottom = self._canvases["bottomspine"]
        top = self._canvases["topspine"]

        ctx = hold_canvas if hold else nullcontext

        with ctx():
            for canvas in (bottom, top):
                canvas.clear()
                # Re-set canvas properties after clear() resets them
                canvas.text_align = "center"
                canvas.fill_style = "black"

            bottom.text_baseline = "top"
            # top.text_baseline = "bottom"

            bottom.begin_path()
            bottom.move_to(0, 0)
            bottom.line_to(self.width, 0)
            bottom.stroke()

            top.begin_path()
            top.move_to(0, top.height)
            top.line_to(self.width, top.height)
            top.stroke()

            for tick, label in zip(xticks_axes, xlabels, strict=True):
                if tick < 0 or tick > 1.0:
                    continue
                # x, y = self._ax.transData.transform((tick, ymin))
                # x = (tick - xmin) / (xmax - xmin) * self.width
                x = tick * self.width
                # Use SVG for better text rendering
                bottom.begin_path()
                bottom.move_to(x, 0)
                bottom.line_to(x, 0 + tick_length)
                bottom.stroke()
                # Label
                bottom.fill_text(label, x, 0 + tick_length + label_offset)

                # top.begin_path()
                # top.move_to(x, top.height)
                # top.line_to(x, top.height - tick_length)
                # top.stroke()

                # string += (
                #     f'<line x1="{x}" y1="0" x2="{x}" y2="7" '
                #     'style="stroke:black;stroke-width:1" />'
                # )
                # string += (
                #     f'<text x="{x}" y="9" text-anchor="middle" dominant-baseline="hanging">'
                #     f"{label}</text>"
                # )

            # string += (
            #     f'<div style="position: absolute; top: 0px; left: {x}px; '
            #     'display: inline-block; padding-top: 2px;">'
            #     '<div style="position: absolute; top: 0; left: 50%; '
            #     "transform: translateX(-50%); width: 1px; height: 7px; "
            #     'background-color: black;"></div>'
            #     f"{label.replace(' ', '&nbsp;')}</div>"
            # )
        # string += "</svg></div>"

        # ticker_ = ticker.AutoLocator()
        # ticks = ticker_.tick_values(left, right)
        # string = '<div style="position: relative; height: 30px;">'
        # precision = max(-round(np.log10(right - left)) + 1, 0)
        # for tick in ticks:
        #     if left + 0.01 * (right - left) <= tick <= right:
        #         x = (tick - left) / (right - left) * self.width - 5
        #         string += (
        #             f'<div style="position: absolute; left: {x}px; top: 4px;">'
        #             f"{value_to_string(tick, precision=precision)}</div>"
        #         )
        #         string += (
        #             f'<div style="position: absolute; left: {x}px;top: -6px">'
        #             "&#9589;</div>"
        #         )
        # string += "</div>"
        # return string

    def _make_yticks(self, hold=True):
        """
        Create tick labels on outline edges
        """
        tick_length = 6
        label_offset = 3

        # (xmin, xmax), (ymin, ymax) = self._ax.get_xlim(), self._ax.get_ylim()
        # ymin, ymax = self.camera.bottom, self.camera.top
        yticks = self.get_yticks()
        ylabels = [lab.get_text() for lab in self.get_yticklabels()]

        xy = np.vstack((np.zeros_like(yticks), yticks)).T
        yticks_axes = self._ax.transAxes.inverted().transform(
            self._ax.transData.transform(xy)
        )[:, 1]

        left = self._canvases["leftspine"]
        right = self._canvases["rightspine"]

        ctx = hold_canvas if hold else nullcontext

        with ctx():
            for canvas in (left, right):
                canvas.clear()
                # Re-set canvas properties after clear() resets them
                canvas.text_baseline = "middle"
                canvas.fill_style = "black"

            left.text_align = "right"
            right.text_align = "left"

            left.begin_path()
            left.move_to(left.width, 0)
            left.line_to(left.width, self.height)
            left.stroke()

            right.begin_path()
            right.move_to(0, 0)
            right.line_to(0, self.height)
            right.stroke()

            for tick, label in zip(yticks_axes, ylabels, strict=True):
                if tick < 0 or tick > 1.0:
                    continue
                # x, y = self._ax.transData.transform((xmin, tick))
                y = self.height - (tick * self.height)
                # Use SVG for better text rendering
                left.begin_path()
                left.move_to(left.width, y)
                left.line_to(left.width - tick_length, y)
                left.stroke()
                # Label
                left.fill_text(label, left.width - tick_length - label_offset, y)

    def get_xlim(self):
        return self._xmin, self._xmax

    def set_xlim(self, left, right=None):
        self._ax.set_xlim(left, right)
        if right is None:
            right = left[1]
            left = left[0]
        self._xmin = left
        self._xmax = right
        self.camera.left = left
        self.camera.right = right
        self._update_ticks_and_layout()

    def get_ylim(self):
        return self._ymin, self._ymax

    def set_ylim(self, bottom, top=None):
        self._ax.set_ylim(bottom, top)
        if top is None:
            top = bottom[1]
            bottom = bottom[0]
        self._ymin = bottom
        self._ymax = top
        self.camera.bottom = bottom
        self.camera.top = top
        self._update_ticks_and_layout()

    def get_xticks(self):
        return self._ax.get_xticks()

    def get_xticklabels(self):
        return self._ax.get_xticklabels()

    def get_yticks(self):
        return self._ax.get_yticks()

    def get_yticklabels(self):
        return self._ax.get_yticklabels()

    def zoom(self, box):
        self._zoom_xmin = box[0]
        self._zoom_xmax = box[1]
        self._zoom_ymin = box[2]
        self._zoom_ymax = box[3]
        self.camera.left = self._zoom_xmin
        self.camera.right = self._zoom_xmax
        self.camera.bottom = self._zoom_ymin
        self.camera.top = self._zoom_ymax
        self._ax.set(
            xlim=(self._zoom_xmin, self._zoom_xmax),
            ylim=(self._zoom_ymin, self._zoom_ymax),
        )
        self._make_xticks(
            # left=self._zoom_xmin, right=self._zoom_xmax
        )
        self._make_yticks(
            # bottom=self._zoom_ymin, top=self._zoom_ymax
        )

    # def _apply_zoom(self):
    #     for artist in self._artists:
    #         artist._apply_transform()

    def reset(self):
        self.camera.left = self._xmin
        self.camera.right = self._xmax
        self.camera.bottom = self._ymin
        self.camera.top = self._ymax
        self._ax.set(xlim=(self._xmin, self._xmax), ylim=(self._ymin, self._ymax))
        self._update_ticks_and_layout()

    def _update_ticks_and_layout(self):
        self._make_xticks(
            # left=self.camera.left, right=self.camera.right
        )
        self._make_yticks(
            # bottom=self.camera.bottom, top=self.camera.top
        )
        # self._update_layout()

    def _update_layout(self):
        return
        areas = ""
        columns = ""
        rows = ""
        if self._title.value:
            areas += (
                f'"{"." if self._ylabel.value else ""} '
                f'{"." if self._leftspine.value else ""} title ."\n'
            )
            rows += "30px "
        if self._topspine.value:
            areas += (
                f'"{"." if self._ylabel.value else ""} '
                f"{'.' if self._leftspine.value else ''} "
                'topspine topspine"\n'
            )
            rows += "35px "
        areas += (
            f'"{"ylabel" if self._ylabel.value else ""} '
            f"{'leftspine' if self._leftspine.value else ''} renderer "
            f'{"rightspine" if self._rightspine.value else "."}"\n'
        )
        rows += f"{self.height}px "
        if self._bottomspine.value:
            areas += (
                f'"{"." if self._ylabel.value else ""} '
                f"{'leftspine' if self._leftspine.value else ''} "
                'bottomspine bottomspine"\n'
            )
            rows += "35px "
        if self._xlabel.value:
            areas += (
                f'"{"." if self._ylabel.value else ""} '
                f"{'.' if self._leftspine.value else ''} "
                f'xlabel {"rightspine" if self._rightspine.value else "."}"'
            )
            rows += "30px"

        columns = (
            f"{'30px' if self._ylabel.value else ''} "
            f"{'80px' if self._leftspine.value else ''} "
            f"{self.width}px 35px"
        )

        self.layout.grid_template_columns = columns
        self.layout.grid_template_rows = rows
        self.layout.grid_template_areas = areas

    def set_figure(self, fig):
        self._fig = fig
        self.width = self._fig.width // self._fig._ncols
        self.height = self._fig.height // self._fig._nrows
        self.renderer.layout.height = f"{self.height}px"
        self.renderer.layout.width = f"{self.width}px"
        self._update_ticks_and_layout()

    def toggle_pan(self, value):
        self.controls.enablePan = value

    def set_xlabel(self, label, fontsize="1.3em"):
        if label:
            self._xlabel.value = (
                '<div style="position:relative; '
                f'width: {self.width}px; height: 30px;">'
                '<div style="position:relative; top: 50%;left: 50%; '
                f"transform: translate(-50%, -50%); font-size: {fontsize};"
                f'float:left;">{label.replace(" ", "&nbsp;")}</div></div>'
            )
        else:
            self._xlabel.value = ""
        self._xlabel._raw_string = label
        self._update_layout()

    def get_xlabel(self):
        return self._xlabel._raw_string

    def set_ylabel(self, label, fontsize="1.3em"):
        if label:
            self._ylabel.value = (
                '<div style="position:relative; '
                f'width: 30px; height: {self.height}px;">'
                '<div style="position:relative; top: 50%;left: 50%; '
                "transform: translate(-50%, -50%) rotate(-90deg); "
                f"font-size: {fontsize};"
                f'float:left;">{label.replace(" ", "&nbsp;")}</div></div>'
            )
        else:
            self._ylabel.value = ""
        self._ylabel._raw_string = label
        self._update_layout()

    def get_ylabel(self):
        return self._ylabel._raw_string

    def set_title(self, title, fontsize="1.3em"):
        if title:
            self._title.value = (
                '<div style="position:relative; '
                f'width: {self.width}px; height: 30px;">'
                '<div style="position:relative; top: 50%;left: 50%; '
                f"transform: translate(-50%, -50%); font-size: {fontsize};"
                f'float:left;">{title.replace(" ", "&nbsp;")}</div></div>'
            )
        else:
            self._title.value = ""
        self._title._raw_string = title
        self._update_layout()

    def get_title(self):
        return self._title._raw_string

    def plot(self, *args, color=None, **kwargs):
        if color is None:
            color = f"C{len(self.lines)}"
        line = Line(*args, color=color, **kwargs)
        self.lines.append(line)
        self.add_artist(line)
        self.autoscale()
        return line

    def scatter(self, *args, color=None, **kwargs):
        if color is None:
            color = f"C{len(self.collections)}"
        coll = Points(*args, color=color, **kwargs)
        self.collections.append(coll)
        self.add_artist(coll)
        self.autoscale()
        return coll

    def imshow(self, *args, **kwargs):
        image = Image(self, *args, **kwargs)
        self.images.append(image)
        self.add_artist(image)
        self.autoscale()
        return image
