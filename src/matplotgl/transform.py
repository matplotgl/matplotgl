class Transform:

    def __init__(self, origin=0, scale=1):

        self.origin = origin
        self.scale = scale
        self.zoomed_origin = None
        self.zoomed_scale = None

    def __call__(self, x):
        if None not in (self.zoomed_origin, self.zoomed_scale):
            return (x - self.zoomed_origin) * self.zoomed_scale
        else:
            return (x - self.origin) * self.scale

    def __repr__(self):
        return f'Transform(origin={self.origin}, scale={self.scale})'

    def inverse(self, x):
        return

    def update(self, low, high):
        self.origin = low
        self.scale = 1.0 / (high - low)

    def zoom(self, low, high):
        self.zoomed_origin = low
        self.zoomed_scale = 1.0 / (high - low)

    def reset(self):
        self.zoomed_origin = None
        self.zoomed_scale = None
