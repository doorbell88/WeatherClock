black           =   (0, 0, 0)
white           =   (255, 255, 255)
red             =   (255, 0, 0)
green           =   (0, 255, 0)
blue            =   (0, 0, 255)
cyan            =   (0, 255, 255)
magenta         =   (255, 0, 255)
yellow          =   (255, 170, 0)
orange          =   (255, 50, 0)
indigo          =   (180, 0, 255)
violet          =   (220, 0, 200)
light_yellow    =   (200, 200, 25)
light_green     =   (75, 255, 75)
dark_green      =   (0, 100, 0)
light_blue      =   (50, 50, 255)
dark_blue       =   (0, 0, 100)
gray_blue       =   (50, 50, 200)
light_gray      =   (100, 100, 100)
gray            =   (50, 50, 50)


# Get lowest nonzero LED value
colors = filter(lambda x: '__' not in x, dir())
lowest = 255
for color in colors:
    c_min = min(eval(color))
    if c_min > 0 and c_min < lowest:
        lowest = c_min

DIMMEST = (255/lowest) + 1
