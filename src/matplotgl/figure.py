from .toolbar import Toolbar

import ipywidgets as ipw
import numpy as np
import pythreejs as p3


class Figure(ipw.GridBox):

    def __init__(self) -> None:

        self.background_color = "#f0f0f0"
        self._axes = []

        # Make background to enable box zoom
        self._background_geometry = p3.BoxGeometry(width=200,
                                                   height=200,
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

        self.width = 700
        self.height = 450
        # self.camera = p3.PerspectiveCamera(position=[0.0, 0, 2],
        #                                    aspect=self.width / self.height)
        # self.camera = p3.OrthographicCamera(-0.1, 1.1, 1.1, -0.1, -1, 100)
        self.camera = p3.OrthographicCamera(-0.001, 1.0, 1.0, -0.001, -1, 100)
        self.scene = p3.Scene(children=[
            self.camera, self._background_mesh, self._zoom_rect_line
        ],
                              background=self.background_color)
        self.controls = p3.OrbitControls(controlling=self.camera,
                                         enableZoom=False)
        self.renderer = p3.Renderer(
            camera=self.camera,
            scene=self.scene,
            controls=[self.controls],
            width=self.width,
            height=self.height,
            # antialiasing=True
        )
        self.toolbar = Toolbar()
        self.toolbar._home.on_click(self.home)
        self.toolbar._zoom.observe(self.toggle_pickers, names='value')
        self._zoom_mouse_down = False
        self._zoom_mouse_moved = False

        self.toolbar.layout = ipw.Layout(grid_area='toolbar')
        self.renderer.layout = ipw.Layout(grid_area='main')

        self.left_bar = ipw.VBox(layout=ipw.Layout(grid_area='left'))
        self.right_bar = ipw.VBox(layout=ipw.Layout(grid_area='right'))
        self.bottom_bar = ipw.HBox(layout=ipw.Layout(grid_area='bottom'))
        self.top_bar = ipw.HBox(layout=ipw.Layout(grid_area='top'))

        # super().__init__([self.toolbar, self.left_bar,
        #     ipw.VBox([self.top_bar, self.renderer, self.bottom_bar]), self.right_bar]),
        #     self.bottom_bar
        # ])

        super().__init__(
            children=[
                self.toolbar, self.renderer, self.left_bar, self.right_bar,
                self.bottom_bar, self.top_bar
            ],
            layout=ipw.Layout(
                grid_template_rows='auto auto auto',
                # grid_template_columns='5% 5% 85% 5%',
                grid_template_columns='40px 40px auto 0px',
                grid_template_areas='''
            ". . top ."
            "toolbar left main right"
            ". . bottom ."
            '''))

    def home(self, *args):
        for ax in self._axes:
            ax.reset()

    def toggle_pickers(self, change):
        if change['new']:
            self._zoom_down_picker.observe(self.on_mouse_down, names=['point'])
            self._zoom_up_picker.observe(self.on_mouse_up, names=['point'])
            self._zoom_move_picker.observe(self.on_mouse_move, names=['point'])
            self.renderer.controls = [
                self.controls, self._zoom_down_picker, self._zoom_up_picker,
                self._zoom_move_picker
            ]
        else:
            self._zoom_down_picker.unobserve_all()
            self._zoom_up_picker.unobserve_all()
            self._zoom_move_picker.unobserve_all()
            self.renderer.controls = [self.controls]

    def on_mouse_down(self, change):
        self._zoom_mouse_down = True
        x, y, z = change['new']
        self._zoom_rect_line.geometry.attributes['position'].array = np.array(
            [[x, x, x, x, x], [y, y, y, y, y], [0, 0, 0, 0, 0]]).T
        self._zoom_rect_line.visible = True
        print(x, y, z, self._zoom_rect_line.visible, self.camera.near,
              self.camera.far)

    def on_mouse_up(self, *ignored):
        if self._zoom_mouse_down:
            self._zoom_mouse_down = False
            self._zoom_rect_line.visible = False
            if self._zoom_mouse_moved:
                array = self._zoom_rect_line.geometry.attributes[
                    'position'].array
                for ax in self._axes:
                    ax.zoom({
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

    def add_axes(self, ax):
        self._axes.append(ax)
        ax.set_figure(self)
        # self.camera.add(ax)
