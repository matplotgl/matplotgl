# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Matplotgl contributors (https://github.com/matplotgl)

from .toolbar import Toolbar
from .widgets import HBar


class Figure(HBar):

    def __init__(self, figsize=(5., 3.5)) -> None:

        self.axes = []
        self._dpi = 96
        self.width = figsize[0] * self._dpi
        self.height = figsize[1] * self._dpi

        self.toolbar = Toolbar()
        self.toolbar._home.on_click(self.home)
        self.toolbar._zoom.observe(self.toggle_pickers, names='value')
        self.toolbar._pan.observe(self.toggle_pan, names='value')

        super().__init__([self.toolbar])

    def home(self, *args):
        for ax in self.axes:
            ax.reset()

    def toggle_pickers(self, change):
        for ax in self.axes:
            if change['new']:
                ax._zoom_down_picker.observe(ax.on_mouse_down, names=['point'])
                ax._zoom_up_picker.observe(ax.on_mouse_up, names=['point'])
                ax._zoom_move_picker.observe(ax.on_mouse_move, names=['point'])
                ax.renderer.controls = [
                    ax.controls, ax._zoom_down_picker, ax._zoom_up_picker,
                    ax._zoom_move_picker
                ]
            else:
                ax._zoom_down_picker.unobserve_all()
                ax._zoom_up_picker.unobserve_all()
                ax._zoom_move_picker.unobserve_all()
                ax.renderer.controls = [ax.controls]

    def toggle_pan(self, change):
        for ax in self.axes:
            ax.toggle_pan(change['new'])

    def add_axes(self, ax):
        self.axes.append(ax)
        ax.set_figure(self)
        self.add(ax)
