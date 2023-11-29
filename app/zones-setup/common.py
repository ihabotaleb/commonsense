class Bounds:
    x = 0
    y = 0
    w = 0
    h = 0

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.h = w
        self.w = h

    def __str__(self):
        return "x: {}, y: {}, w: {}, h: {}".format(self.x, self.y, self.w, self.h)
    
    def __repr__(self):
        return "x: {}, y: {}, w: {}, h: {}".format(self.x, self.y, self.w, self.h)
    
    def __eq__(self, other):
        return self.x == other.x and self.y and other.y and self.w == other.w and self.h == other.h
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def to_dict(self):
        return {'x': self.x, 'y': self.y, 'w': self.w, 'h': self.h}
    

def get_bounded_image(frame, ref, bounds):
    return frame[bounds.y:bounds.y+bounds.h, bounds.x:bounds.x+bounds.w], ref[bounds.y:bounds.y+bounds.h, bounds.x:bounds.x+bounds.w]

def get_bounded_image(frame, bounds):
    return frame[bounds.y:bounds.y+bounds.h, bounds.x:bounds.x+bounds.w]