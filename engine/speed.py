


'''
contains the data pertinent to each game speed.


animationCoefficient:
    animation duration is set to 0.2.
    animationCoefficient is multiplied to time to produce
    the animation speed desired. 
    divide duration by coefficient to get actual animation duration
    TODO make animation duration stuff more sensical
'''

class Speed(object):
    def __init__(self, animCoefficient, delay, name):
        self.animCoefficient = animCoefficient
        self.delay = delay
        self.name = name
        self.lastTs = 0
    

PAUSED = Speed(0, 999, "Paused")
SLOW = Speed(0.34, 0.6, "Slow")
NORMAL = Speed(1.5, 0.3, "Normal")
FAST = Speed(5, 0.1, "Fast")
SUPER_FAST = Speed(10, 0.02, "Super Fast")