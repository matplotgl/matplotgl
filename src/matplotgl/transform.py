class Transform:

    def __init__(self, origin=0, scale=1):

        self.origin = origin
        self.scale = scale

    def to_window(self, x):
        return (x - self.origin) * self.scale
