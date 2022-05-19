##concatenate videos and insert blank

#import exiftool
from moviepy.editor import *
import os
#import datetime
#import pytz 


blank_size = (1920, 1080)
blank_color=(0,0,0)

clip1 = VideoFileClip("PC3_V1_20220422.mp4")
#clip2 = VideoFileClip("PC2_V2_20220303.mp4")
clip2 = ColorClip(blank_size, blank_color, duration = clip1.duration)

clip3 = VideoFileClip("PC3_V3_20220422.mp4")
clip4 = VideoFileClip("PC3_V4_20220422.mp4")

final_clip = clips_array([[clip1, clip2],
                          [clip3, clip4]])
final_clip.write_videofile("PC3_20220422_stack.mp4")

