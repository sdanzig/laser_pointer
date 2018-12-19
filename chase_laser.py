#!/usr/bin/env python3

import anki_vector
import numpy
import time
from anki_vector.util import degrees, distance_mm, speed_mmps
from matplotlib import pyplot as plt

MIN_X = 0
MIN_Y = 0
MAX_X = 639
MAX_Y = 359
GREEN_MIN = 120
GREENER_THRESHOLD = 1
meow_said = False

def pixel_is_green(p):
    ret = True
    if p[1] < GREEN_MIN:
        ret = False
    elif p[0] > (p[1] - GREENER_THRESHOLD):
        ret = False
    elif p[2] > (p[1] - GREENER_THRESHOLD):
        ret = False
    return ret

def pixel_at_coord_is_green(image, x, y):
#    print("Checking ", x, y, image[y][x][0], image[y][x][1], image[y][x][2])
    return pixel_is_green(image[y][x])

def green_splotch_detected(image, x, y):
    if not pixel_at_coord_is_green(image, x, y):
        return False
    print("Green pixel detected, rgb = (", image[y][x][0], image[y][x][1], image[y][x][2], ")")
    if x > 0 and pixel_at_coord_is_green(image, x - 1, y):
        print("Green pixel found to left. Splotch detected!")
        return True
    if y > 0 and pixel_at_coord_is_green(image, x, y - 1):
        print("Green pixel found below. Splotch detected!")
        return True
    if x < MAX_X and pixel_at_coord_is_green(image, x + 1, y):
        print("Green pixel found to right. Splotch detected!")
        return True
    if y < MAX_Y and pixel_at_coord_is_green(image, x, y + 1):
        print("Green pixel found above. Splotch detected!")
        return True
    print("No neighboring green pixels found.")
    return False

def green_splotch_detected_in_area(image, min_x, max_x, min_y, max_y):
    for x in range(min_x, max_x, 2):
        for y in range(min_y, max_y, 2):
            if green_splotch_detected(image, x, y):
                return True
    return False


def main():
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial, enable_camera_feed=True) as robot:
        def turn_left():
            robot.behavior.turn_in_place(degrees(20))

        def turn_far_left():
            robot.behavior.turn_in_place(degrees(40))

        def turn_right():
            robot.behavior.turn_in_place(degrees(-20))

        def turn_far_right():
            robot.behavior.turn_in_place(degrees(-40))

        def chase():
            robot.behavior.drive_straight(distance_mm(200), speed_mmps(300))

        stop = False
        robot.behavior.set_head_angle(degrees(-5))
        print("Starting chase...")
        while not stop:
            pil_image = robot.camera.latest_image
            image = numpy.array(pil_image)
#            plt.imshow(image, interpolation='nearest')
#            plt.show()

            if green_splotch_detected_in_area(image, MIN_X, 127, MIN_Y, 89):
                print("Spotted dot nearby, to the far left")
                turn_far_left()
                meow_said = False
            elif green_splotch_detected_in_area(image, 127, 255, MIN_Y, 89):
                print("Spotted dot nearby, to the left")
                turn_left()
                meow_said = False
            elif green_splotch_detected_in_area(image, 255, 383, MIN_Y, 89):
                print("Captured the dot!")
                if not meow_said:
                    robot.say_text("Meeow")
                    meow_said = True
            elif green_splotch_detected_in_area(image, 383, 511, MIN_Y, 89):
                print("Spotted dot nearby, to the right")
                turn_right()
                meow_said = False
            elif green_splotch_detected_in_area(image, 511, MAX_X, MIN_Y, 89):
                print("Spotted dot nearby, to the far right")
                turn_far_right()
                meow_said = False
            elif green_splotch_detected_in_area(image, MIN_X, 127, 90, MAX_Y):
                print("Spotted dot in the distance, to the far left")
                turn_far_left()
                chase()
                meow_said = False
            elif green_splotch_detected_in_area(image, 127, 255, 90, MAX_Y):
                print("Spotted dot in the distance, to the left")
                turn_left()
                chase()
                meow_said = False
            elif green_splotch_detected_in_area(image, 255, 383, 90, MAX_Y):
                print("Spotted dot in the distance, straight ahead")
                chase()
                meow_said = False
            elif green_splotch_detected_in_area(image, 383, 511, 90, MAX_Y):
                print("Spotted dot in the distance, to the right")
                turn_right()
                chase()
                meow_said = False
            elif green_splotch_detected_in_area(image, 511, MAX_X, 90, MAX_Y):
                print("Spotted dot in the distance, to the far right")
                turn_far_right()
                chase()
                meow_said = False


if __name__ == '__main__':
    main()
