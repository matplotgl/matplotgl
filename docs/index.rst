*********************************************
Matplotgl - Matplotlib for Jupyter with WebGL
*********************************************

Matplotgl is a drop-in replacement for Matplotlib's ``pyplot`` module
that uses Pythreejs to render graphics in Jupyter using the
`three.js <https://threejs.org/>`_` library.

Matplotgl is still highly experimental, and only a small part of Matplotlib's
functionality is currently implemented.

Installation
============

You can install from ``pip`` using

.. code-block:: sh

   pip install matplotgl

Example
=======

.. code-block:: python

   import matplotgl as plt

   fig, ax = plt.subplots()

   x = np.arange(100.)
   y = np.sin(0.1 * x)

   ax.plot(x, y, lw=2)
   ax.set_xlabel('Time (seconds)')
   ax.set_ylabel('Amplitude (cm)')

   fig

.. toctree::
   :maxdepth: 1
   :hidden:

   plot

.. toctree::
   :maxdepth: 2
   :hidden:

   api

.. toctree::
   :hidden:

   Release notes <https://github.com/matplotgl/matplotgl/releases>
