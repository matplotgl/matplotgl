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


class Figure:

    def __init__(self) -> None:

        self.width = 800
        self.height = 500
        self.camera = p3.PerspectiveCamera(position=[0.0, 0, 2],
                                           aspect=self.width / self.height)
        # self.camera = p3.OrthographicCamera(-2, 2, -2, 2)
        self.scene = p3.Scene(children=[self.camera], background="#f0f0f0")
        self.controls = p3.OrbitControls(controlling=self.camera)
        self.renderer = p3.Renderer(camera=self.camera,
                                    scene=self.scene,
                                    controls=[self.controls],
                                    width=self.width,
                                    height=self.height)

    def add_axes(self, axes):
        self.scene.add(axes)


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