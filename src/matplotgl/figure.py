from .toolbar import Toolbar

import ipywidgets as ipw
import numpy as np
import pythreejs as p3

# N = 1000

# # geometry = p3.BufferGeometry(
# #     attributes={
# #         'position':|
# #         p3.BufferAttribute(array=20.0 * (np.random.random((N, 3)) - 0.5).astype('float32')),
# #         'color':
# #         p3.BufferAttribute(array=np.zeros([N, 3], dtype='float32'))
# #     })

# # geometry = p3.BoxGeometry(
# #     width=20,
# #     height=15,
# #     widthSegments=1,
# #     heightSegments=1)

# geometry = p3.BoxGeometry(width=200,
#                           height=200,
#                           widthSegments=1,
#                           heightSegments=1)

# # material = p3.PointsMaterial(vertexColors='VertexColors', size=5)
# material = p3.MeshBasicMaterial(color='red', side='DoubleSide')

# mesh = p3.Mesh(geometry=geometry, material=material)
# # mesh.rotateY(0.5 * np.pi)


class Figure(ipw.HBox):

    def __init__(self) -> None:

        background_color = "#f0f0f0"

        # Make background to enable box zoom
        self._background_geometry = p3.BoxGeometry(width=200,
                                                   height=200,
                                                   widthSegments=1,
                                                   heightSegments=1)
        self._background_material = p3.MeshBasicMaterial(
            color=background_color, side='DoubleSide')
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

        self.width = 800
        self.height = 500
        # self.camera = p3.PerspectiveCamera(position=[0.0, 0, 2],
        #                                    aspect=self.width / self.height)
        self.camera = p3.OrthographicCamera(-0.1, 1.1, 1.1, -0.1, -1, 100)
        self.scene = p3.Scene(children=[
            self.camera, self._background_mesh, self._zoom_rect_line
        ],
                              background=background_color)
        self.controls = p3.OrbitControls(controlling=self.camera)
        self.renderer = p3.Renderer(camera=self.camera,
                                    scene=self.scene,
                                    controls=[self.controls],
                                    width=self.width,
                                    height=self.height)
        self.toolbar = Toolbar()
        self.toolbar._home.on_click(self.home)
        self.toolbar._zoom.observe(self.toggle_pickers, names='value')
        self._zoom_mouse_down = False

        super().__init__([self.toolbar, self.renderer])

    def home(self, *args):
        self.camera.left = -0.1
        self.camera.right = 1.1
        self.camera.bottom = -0.1
        self.camera.top = 1.1

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
        print(x, y, z, self._zoom_rect_line.visible)

    def on_mouse_up(self, *ignored):
        if self._zoom_mouse_down:
            self._zoom_mouse_down = False
            self._zoom_rect_line.visible = False
            array = self._zoom_rect_line.geometry.attributes['position'].array
            self.camera.left = array[:, 0].min()
            self.camera.right = array[:, 0].max()
            self.camera.bottom = array[:, 1].min()
            self.camera.top = array[:, 1].max()

    def on_mouse_move(self, change):
        if self._zoom_mouse_down:
            x, y, z = change['new']
            new_pos = self._zoom_rect_line.geometry.attributes[
                'position'].array.copy()
            new_pos[2:4, 0] = x
            new_pos[1:3, 1] = y
            self._zoom_rect_line.geometry.attributes[
                'position'].array = new_pos

    def add_axes(self, axes):
        axes._fig = self
        self.camera.add(axes)


# # Picker object
# down_picker = p3.Picker(controlling=mesh, event='mousedown')
# up_picker = p3.Picker(controlling=mesh, event='mouseup')
# move_picker = p3.Picker(controlling=mesh, event='mousemove')
# renderer.controls = renderer.controls + [down_picker, up_picker, move_picker]

# def on_mouse_down(change):
#     print("mouse DOWN")
#     print(down_picker.point)

# def on_mouse_up(change):
#     print("mouse UP")
#     print(up_picker.point)

# def on_mouse_move(change):
#     print("mouse MOVE")
#     print(move_picker.point)

# down_picker.observe(on_mouse_down, names=['point'])
# up_picker.observe(on_mouse_up, names=['point'])
# move_picker.observe(on_mouse_move, names=['point'])