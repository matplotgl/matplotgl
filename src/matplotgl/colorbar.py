from matplotlib.colorbar import ColorbarBase
import matplotlib.pyplot as pyp


def fig_to_bytes(fig) -> bytes:
    """
    Convert a Matplotlib figure to svg bytes.

    Parameters
    ----------
    fig:
        The figure to be converted.
    """
    from io import BytesIO

    buf = BytesIO()
    fig.savefig(buf, format="svg", bbox_inches="tight")
    buf.seek(0)
    return buf.getvalue()


def make_colorbar(mappable, height_inches: float) -> str:
    fig = pyp.Figure(figsize=(height_inches * 0.2, height_inches))
    cax = fig.add_axes([0.05, 0.02, 0.2, 0.98])
    ColorbarBase(cax, cmap=mappable.cmap)  # , norm=self.normalizer)
    return fig_to_bytes(fig).decode()
