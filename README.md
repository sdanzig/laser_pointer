# laser_pointer
Enables Anki Vector to chase a laser pointer.  See a rather dark demonstration here: https://youtu.be/XcUQncacbnQ

This is very rudimentary.  I'm just learning what I can do with the Anki Vector, and certainly am not a computer vision expert.

I convert the pillow image from Anki Vector to a numpy array, then use x/y coords to get the RGB values of the 200k+ pixels.  I figured there'd either be a bright green spot, or perhaps a white spot, if the pixel got overexposed entirely.  I was able to use matplotlib to see the photo, and it conveniently lets me hover the mouse over a pixel and see the RGB values.  I saw that the green values are at a minimum of 200 or so, ranging up to 255, and some of the red/blue values are clipped as well, but usually they're 20-40 less.  I tried scanning for a pixel with that profile.  I also try to find a similar neighboring pixel, just to try to eliminate noise.  This probably makes Vector a little more picky with what he chases.

There's a bunch of problems that makes this not work perfectly.  You'd think a bright shining dot would stand out from its surroundings, but Vector's camera and processing results in moderately lit white walls being read in at pixel values as high as 255,255,255.  There's no way I see yet using the Vector SDK to turn off its auto-exposure adjustments.  Right now, the most reliable way for Vector to detect the bright dot is to turn off the lights.  I figure I can maybe do some detection of the dimensions and surrounding contrast of a bright dot.

For control of the robot, I split up the image from Vector's camera into 10 blocks, with the 640 columns divided into fifths, and the 360 rows divided into bottom fourth and top three-fourth sections.

The middle fifth of the screen is straight ahead.  The fifth of the screen to the right and left of that results in a 20 degree corresponding turn, and the fifths on the edges are far right and far left, making the vector turn 40 degrees.  I probably should detect the dot in the entire screen  at once, and do some basic geometry to determine how many degrees to turn.  Future upgrade.

The bottom fourth of the screen is detected as "near", and the top 3/4ths is detected as "in the distance". Vector will move forward if the dot is in the distance, and if the dot is detected as near and straight ahead, he will meow like a kitty.  This is a rather unreliable mechanism to detect distance, as dot can be in the lower fourth of the screen and still a decent distance away.  I think using the range finder will be a better way to implement that feature.
