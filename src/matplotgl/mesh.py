# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

import pythreejs as p3
import matplotlib as mpl
import numpy as np


class Mesh:
    def __init__(self, *args, cmap="viridis"):
        if len(args) not in (1, 3):
            raise ValueError("Invalid number of arguments: expected 1 or 3.")
        if len(args) == 3:
            x, y, c = args
        elif len(args) == 1:
            c = args[0]
            N, M = c.shape
            x = np.arange(M + 1)
            y = np.arange(N + 1)

        self._cmap = mpl.colormaps[cmap]
        colors_rgba = self._cmap(c.flatten())
        colors = colors_rgba[:, :3].astype("float32")

        # Create meshgrid for all cell corners
        i_indices = np.arange(N)
        j_indices = np.arange(M)
        j_grid, i_grid = np.meshgrid(j_indices, i_indices, indexing="ij")

        # Flatten to get all cells
        i_flat = i_grid.ravel()
        j_flat = j_grid.ravel()
        n_cells = len(i_flat)

        # Create all four corners for all cells at once
        # Each cell has 4 vertices: bottom-left, bottom-right, top-right, top-left
        x_left = x[i_flat]
        x_right = x[i_flat + 1]
        y_bottom = y[j_flat]
        y_top = y[j_flat + 1]

        # Build vertices array (n_cells * 4 vertices, each with x, y, z coords)
        self._vertices = np.zeros((n_cells * 4, 3), dtype=np.float32)
        self._vertices[0::4, 0] = x_left
        self._vertices[0::4, 1] = y_bottom
        self._vertices[1::4, 0] = x_right
        self._vertices[1::4, 1] = y_bottom
        self._vertices[2::4, 0] = x_right
        self._vertices[2::4, 1] = y_top
        self._vertices[3::4, 0] = x_left
        self._vertices[3::4, 1] = y_top
        # z coordinates are already 0

        # Create faces (indices into vertices array)
        # For each cell, create two triangles
        base_indices = np.arange(n_cells) * 4
        faces = np.zeros((n_cells * 2, 3), dtype=np.uint32)
        # First triangle: v0, v1, v2
        faces[0::2, 0] = base_indices
        faces[0::2, 1] = base_indices + 1
        faces[0::2, 2] = base_indices + 2
        # Second triangle: v0, v2, v3
        faces[1::2, 0] = base_indices
        faces[1::2, 1] = base_indices + 2
        faces[1::2, 2] = base_indices + 3

        # Assign colors to vertices (each vertex in a cell gets the same color)
        vertex_colors = np.repeat(colors, 4, axis=0)  # 4 vertices per cell

        # Create BufferGeometry
        geometry = p3.BufferGeometry(
            attributes={
                "position": p3.BufferAttribute(array=self._vertices),
                "color": p3.BufferAttribute(array=vertex_colors),
            },
            index=p3.BufferAttribute(array=faces.ravel()),
        )

        # Create material with vertex colors
        material = p3.MeshBasicMaterial(vertexColors="VertexColors", side="DoubleSide")

        # Create mesh
        self._mesh = p3.Mesh(geometry=geometry, material=material)

    def get_bbox(self):
        return {
            "left": self._vertices[:, 0].min(),
            "right": self._vertices[:, 0].max(),
            "bottom": self._vertices[:, 1].min(),
            "top": self._vertices[:, 1].max(),
        }

    def get(self):
        return self._mesh
