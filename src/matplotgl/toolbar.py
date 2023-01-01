import ipywidgets as ipw


class Toolbar(ipw.VBox):

    def __init__(self) -> None:
        self._zoom = ipw.ToggleButton(icon='square-o', width='40px')
        super().__init__([self._zoom])
