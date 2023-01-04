# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

from .transform import Transform
from .utils import value_to_string

import pythreejs as p3
from matplotlib import ticker
import numpy as np
from typing import List, Tuple

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


# def _get_offsets(limits: Tuple[float], axis: int, ind: int) -> np.ndarray:
#     """
#     Compute offsets for n dimensions, along the edges of the box.
#     """
#     offsets = np.array([limits[i][ind] for i in range(3)])
#     print(offsets, axis)
#     offsets[axis] = -0.05
#     return offsets

# def _make_ticklabels(self, limits: Tuple[Variable, Variable, Variable],
#                      center: List[float], tick_size: float) -> p3.Group:
#     """
#     Create axes labels (coord dimension and unit) on outline edges
#     """
#     labels_group = p3.Group()
#     for axis in range(3):
#         axis_label = f'{limits[axis].dim} [{limits[axis].unit}]'
#         # Offset labels 5% beyond axis ticks to reduce overlap
#         delta = 0.05
#         labels_group.add(
#             _make_sprite(
#                 string=axis_label,
#                 position=(np.roll([1, 0, 0], axis) * center[axis] +
#                           (1.0 + delta) * _get_offsets(limits, axis, 0) -
#                           delta * _get_offsets(limits, axis, 1)).tolist(),
#                 size=tick_size * 0.3 * len(axis_label)))

#     return labels_group

# def _get_delta(x: Variable, axis: int) -> float:
#     """
#     Compute the difference between two bounds along a given axis.
#     """
#     return (x[axis][1] - x[axis][0])

# def _get_offsets(limits: Tuple[Variable, Variable, Variable], axis: int,
#                  ind: int) -> np.ndarray:
#     """
#     Compute offsets for 3 dimensions, along the edges of the box.
#     """
#     offsets = np.array([limits[i][ind] for i in range(3)])
#     offsets[axis] = 0
#     return offsets

# def _make_geometry(
#         limits: Tuple[Variable, Variable, Variable]) -> p3.EdgesGeometry:
#     """
#     Make a geometry to represent the edges of a cubic box.
#     """
#     return p3.EdgesGeometry(
#         p3.BoxBufferGeometry(width=_get_delta(limits, axis=0),
#                              height=_get_delta(limits, axis=1),
#                              depth=_get_delta(limits, axis=2)))


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

        self._geometry = p3.BufferGeometry(
            attributes={
                'position':
                p3.BufferAttribute(array=np.array(
                    [[0, 0, 1, 1, 0], [0, 1, 1, 0, 0], [0, 0, 0, 0, 0]],
                    dtype='float32').T),
            })
        self._material = p3.LineBasicMaterial(color='black', linewidth=1)
        self._outline = p3.Line(geometry=self._geometry,
                                material=self._material)

        limits = [[self.xmin, self.xmax], [self.ymin, self.ymax], [0, 0]]
        self._tick_size = 0.05
        self.ticks = self._make_ticks(limits=limits)
        # self.ticklabels = _make_labels(limits=limits,
        #                                center=center,
        #                                tick_size=tick_size)

        super().__init__()
        for obj in (self._outline, self.ticks):  # , self.ticklabels):
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

        # self.zoom({'left': xmin, 'right': xmax, 'bottom': ymin, 'top': ymax})

        #     # if artist is not None:
        self._transformx.update(low=xmin, high=xmax)
        self._transformy.update(low=ymin, high=ymax)
        self._apply_zoom()
        # {
        #     'left': xmin,
        #     'right': xmax,
        #     'bottom': ymin,
        #     'top': ymax
        # })

    # def apply_
    #     for artist in self._artists:
    #         artist._apply_transform()
    #     self.remove(self.ticks)
    #     self.ticks = self._make_ticks(
    #         limits=[[xmin, xmax], [ymin, ymax], [0, 0]])
    #     self.add(self.ticks)

    def add_artist(self, artist):
        # self.autoscale(artist)
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


# class Outline(p3.Group):
#     """
#     Create an object that draws a rectangular outline, given some limits for the XYZ
#     dimensions. Along the lower edges of the cube are added some tick labels and axes
#     labels, according to the dimension extents, dimension names, and units given in
#     the limits.

#     Parameters
#     ----------
#     limits:
#         A tuple of variables, each of length 2, which contain the lower and upper bounds
#         for the outline. Each variable also has a dimension, which is to be used as the
#         dimension for that direction, as well as a unit, which will be used to label
#         the corresponding axis.
#     tick_size:
#         A number to scale the tick size.
#     """

#     def __init__(self,
#                  limits: Tuple[Variable, Variable, Variable],
#                  tick_size: float = None):

#         center = [var.mean() for var in limits]
#         if tick_size is None:
#             tick_size = 0.05 * np.mean([_get_delta(limits, axis=i) for i in range(3)])

#         self.box = p3.LineSegments(geometry=_make_geometry(limits),
#                                    material=p3.LineBasicMaterial(color='#000000'),
#                                    position=center)

#         self.ticks = self._make_ticks(limits=limits, tick_size=tick_size)
#         self.labels = self._make_labels(limits=limits,
#                                         center=center,
#                                         tick_size=tick_size)

#         super().__init__()
#         for obj in (self.box, self.ticks, self.labels):
#             self.add(obj)

#     def _make_ticks(self, limits: Tuple[Variable, Variable, Variable],
#                     tick_size: float) -> p3.Group:
#         """
#         Create tick labels on outline edges
#         """
#         ticks_group = p3.Group()
#         iden = np.identity(3, dtype=np.float32)
#         ticker_ = ticker.MaxNLocator(5)
#         for axis in range(3):
#             ticks = ticker_.tick_values(limits[axis][0], limits[axis][1])
#             for tick in ticks:
#                 if limits[axis][0] <= tick <= limits[axis][1]:
#                     tick_pos = iden[axis] * tick + _get_offsets(limits, axis, 0)
#                     ticks_group.add(
#                         _make_sprite(string=value_to_string(tick, precision=1),
#                                      position=tick_pos.tolist(),
#                                      size=tick_size))
#         return ticks_group

#     def _make_labels(self, limits: Tuple[Variable, Variable, Variable],
#                      center: List[float], tick_size: float) -> p3.Group:
#         """
#         Create axes labels (coord dimension and unit) on outline edges
#         """
#         labels_group = p3.Group()
#         for axis in range(3):
#             axis_label = f'{limits[axis].dim} [{limits[axis].unit}]'
#             # Offset labels 5% beyond axis ticks to reduce overlap
#             delta = 0.05
#             labels_group.add(
#                 _make_sprite(string=axis_label,
#                              position=(np.roll([1, 0, 0], axis) * center[axis] +
#                                        (1.0 + delta) * _get_offsets(limits, axis, 0) -
#                                        delta * _get_offsets(limits, axis, 1)).tolist(),
#                              size=tick_size * 0.3 * len(axis_label)))

#         return labels_group

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