#!/usr/bin/env python3

import anki_vector
import numpy
import keyboard
from anki_vector.util import degrees, distance_mm, speed_mmps
from matplotlib import pyplot as plt

MIN_X = 0
MIN_Y = 0
MAX_X = 639
MAX_Y = 359
RED_MIN = 140
REDDER_THRESHOLD = 0
LASER_BOUNDARY_THRESHOLD = 20
LASER_RADIUS = 15

def pixel_is_red(p):
    ret = True
    if p[1] < RED_MIN:
        ret = False
    elif p[1] > (p[0] - REDDER_THRESHOLD):
        ret = False
    elif p[2] > (p[0] - REDDER_THRESHOLD):
        ret = False
    return ret

def pixel_is_different(new, old):
    for i in range(0, 2):
        if abs(new[i] - old[i]) > CHANGE_THRESHOLD:
            return True
    return False

def pixel_at_coord_is_red(image, x, y):
#    print("Checking ", x, y, image[y][x][0], image[y][x][1], image[y][x][2])
    return pixel_is_red(image[y][x])

def red_splotch_detected(image, x, y):
    if not pixel_at_coord_is_red(image, x, y):
        return False
    return True
    print("Red pixel detected, rgb = (", image[y][x][0], image[y][x][1], image[y][x][2], ")")
    if x > 0 and pixel_at_coord_is_red(image, x - 1, y):
        print("Red pixel found to left. Splotch detected!")
        return True
    if y > 0 and pixel_at_coord_is_red(image, x, y - 1):
        print("Red pixel found above. Splotch detected!")
        return True
    if x < MAX_X and pixel_at_coord_is_red(image, x + 1, y):
        print("Red pixel found to right. Splotch detected!")
        return True
    if y < MAX_Y and pixel_at_coord_is_red(image, x, y + 1):
        print("Red pixel found below. Splotch detected!")
        return True
    print("No neighboring Red pixels found.")
    return False

def pixel_is_darker(image, x1, y1, x2, y2):
    return image[y1][x1][0] - image[y2][x2][0] > LASER_BOUNDARY_THRESHOLD

def left_is_darker(image, x, y):
    return (x - LASER_RADIUS < MIN_X) or pixel_is_darker(image, x, y, x-LASER_RADIUS, y)

def right_is_darker(image, x, y):
    return (x + LASER_RADIUS > MAX_X) or pixel_is_darker(image, x, y, x+LASER_RADIUS, y)

def up_is_darker(image, x, y):
    return (y - LASER_RADIUS < MIN_Y) or pixel_is_darker(image, x, y, x, y-LASER_RADIUS)

def down_is_darker(image, x, y):
    return (y + LASER_RADIUS > MAX_Y) or pixel_is_darker(image, x, y, x, y+LASER_RADIUS)

def pixel_surrounded_by_dark(image, x, y):
    if left_is_darker(image, x, y) and right_is_darker(image, x, y) and up_is_darker(image, x, y) and down_is_darker(image, x, y):
        return True
    return False

def red_splotch_detected_in_area(image, min_x, max_x, min_y, max_y):
    for x in range(min_x, max_x, 2):
        for y in range(min_y, max_y, 2):
            if red_splotch_detected(image, x, y):
                if pixel_surrounded_by_dark(image, x, y):
                    return True
    return False


def retrieve_new_image(robot):
    pil_image = robot.camera.latest_image
    return numpy.array(pil_image)

def rotate_to_next_head_position(current_head_angle):
    head_pos_map = {
        5 : 0,
        0 : -5,
        -5: -10,
        -10: -15,
        -15: -20,
        -20: 5
    }
    return head_pos_map.get(current_head_angle, 0)

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
        head_angle = -5
        print("Starting chase...")
        countdown = 5
        meow_said = False
        while not stop:
            robot.behavior.set_head_angle(degrees(head_angle))
            image = retrieve_new_image(robot)

            moved = True
            if red_splotch_detected_in_area(image, MIN_X, 127, 270, MAX_Y):
                print("Spotted dot nearby, to the far left")
                turn_far_left()
                meow_said = False
            elif red_splotch_detected_in_area(image, 127, 255, 270, MAX_Y):
                print("Spotted dot nearby, to the left")
                turn_left()
                meow_said = False
            elif red_splotch_detected_in_area(image, 255, 383, 270, MAX_Y):
                print("Captured the dot!")
                if not meow_said:
                    robot.say_text("Meeow")
                    meow_said = True
                    moved = False
            elif red_splotch_detected_in_area(image, 383, 511, 270, MAX_Y):
                print("Spotted dot nearby, to the right")
                turn_right()
                meow_said = False
            elif red_splotch_detected_in_area(image, 511, MAX_X, 270, MAX_Y):
                print("Spotted dot nearby, to the far right")
                turn_far_right()
                meow_said = False
            elif red_splotch_detected_in_area(image, MIN_X, 127, MIN_Y, 269):
                print("Spotted dot in the distance, to the far left")
                turn_far_left()
                chase()
                meow_said = False
            elif red_splotch_detected_in_area(image, 127, 255, MIN_Y, 269):
                print("Spotted dot in the distance, to the left")
                turn_left()
                chase()
                meow_said = False
            elif red_splotch_detected_in_area(image, 255, 383, MIN_Y, 269):
                print("Spotted dot in the distance, straight ahead")
                chase()
                meow_said = False
            elif red_splotch_detected_in_area(image, 383, 511, MIN_Y, 269):
                print("Spotted dot in the distance, to the right")
                turn_right()
                chase()
                meow_said = False
            elif red_splotch_detected_in_area(image, 511, MAX_X, MIN_Y, 269):
                print("Spotted dot in the distance, to the far right")
                turn_far_right()
                chase()
                meow_said = False
            else:
                moved = False
            if not moved:
                countdown = countdown - 1
                if countdown == 0:
                    countdown = 1
                    head_angle = rotate_to_next_head_position(head_angle)
            if keyboard.is_pressed('x'):
                plt.imshow(image, interpolation='nearest')
                plt.show()
                keyboard.clear_all_hotkeys()


if __name__ == '__main__':
    main()
