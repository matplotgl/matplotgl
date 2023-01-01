# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

import pythreejs as p3
from matplotlib import ticker
import numpy as np
from typing import List, Tuple


class Line:

    def __init__(self, x, y, color=) -> None:

        self._geometry = p3.BufferGeometry(
            attributes={
                'position': np.array([x, y, np.zeros_like(x)]),
            })
        self._material = p3.LineBasicMaterial(color='black', linewidth=1)
        self._outline = p3.Line(geometry=self._geometry,
                                material=self._material)

        limits = [[self.xmin, self.xmax], [self.ymin, self.ymax], [0, 0]]
        tick_size = 0.05

        self.ticks = _make_ticks(limits=limits, tick_size=tick_size)
        # self.ticklabels = _make_labels(limits=limits,
        #                                center=center,
        #                                tick_size=tick_size)

        super().__init__()
        for obj in (self._outline, self.ticks):  # , self.ticklabels):
            self.add(obj)


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