##concatenate videos and insert blank

import exiftool
from moviepy.editor import *
import os
import datetime
import pytz 


data_folder = "../PC2/"
###copy paste from PC2.csv file, first row and last row, year, month, day, hour (24-format), minute
local_timezone = 'America/Chicago'

days_start_end = {
    '20220303': [pytz.timezone(local_timezone).localize(datetime.datetime(2022, 3, 3, 17, 54)), pytz.timezone(local_timezone).localize(datetime.datetime(2022, 3, 3, 19, 39))],
    '20220304': [pytz.timezone(local_timezone).localize(datetime.datetime(2022, 3, 4, 7, 5)), pytz.timezone(local_timezone).localize(datetime.datetime(2022, 3, 4, 20, 21))]

}


v_folders = [item for item in os.listdir(data_folder) if item.startswith('V')]
blank_size = (1920, 1080)
blank_color=(0,0,0)
fps = 15
#'Composite:ImageSize': '1920 1080', 'QuickTime:VideoFrameRate': 15




for v_folder in v_folders:
    video_files = {}
    video_files_start = {}
    days = []
    for root, dirs, files in os.walk(data_folder + v_folder):

        for item in files:
            if item.endswith('.mp4') and not item.startswith('.') and item[0].isnumeric():
                root = root.replace('\\', '/')
                day = root.split('/')[3]
                if day not in days:
                    days.append(day)
                    video_files[day] = [root + '/' + item]
                    
                else:
                    video_files[day].append(root + '/' + item)


    for day in days:

        print(day)

        global_start_utc = temp_start = days_start_end[day][0].astimezone(pytz.utc)
        global_end_utc = temp_end = days_start_end[day][1].astimezone(pytz.utc)

        two_hour_chunks = []
        ##2 hour chunks
        while (temp_end - temp_start).total_seconds() > 7200: ##when there are 2 hours
            if temp_start.hour + 2 <= 23:
                temp_time = temp_start.replace(second=0, minute=0, hour = temp_start.hour + 2)
            else:
                temp_time = temp_start.replace(second=0, minute=0, day = temp_start.day + 1, hour = (temp_start.hour + 2) % 24)
            two_hour_chunks.append([temp_start, temp_time])
            temp_start = temp_time

        if (temp_end - temp_start).total_seconds() > 0:
            two_hour_chunks.append([temp_start, temp_end])

        print(global_start_utc, global_end_utc)
        print(two_hour_chunks)


        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(video_files[day])

        video_files_start[day] = []

        for item in metadata:
            video_files_start[day].append(datetime.datetime.strptime(item['QuickTime:CreateDate'] + ' +0000', '%Y:%m:%d %H:%M:%S %z'))
            #video_files_duration.append(item['QuickTime:Duration']) 

        video_files_start_day, video_files_day = zip(*sorted(zip(video_files_start[day], video_files[day])))

        #video_files_day = video_files_day[:4]
        #video_files_start_day = video_files_start_day[:4]

        pointer = 0
        for this_start, this_end in two_hour_chunks:
            chunk_starting = True

            for i in range(pointer, len(video_files_day)):
                if chunk_starting:
                    clip1 = None
                else:
                    clip1 = merge

                clip2 = VideoFileClip(video_files_day[i])
                if video_files_start_day[i] >= this_end:
                    break

                print(this_start, this_end, video_files_start_day[i])

                if chunk_starting:
                    time_difference = video_files_start_day[i] - this_start
                    
                else:
                    time_difference = video_files_start_day[i] - (this_start + datetime.timedelta(seconds = clip1.duration))
                
                print(time_difference.total_seconds())

                if time_difference.total_seconds() < 0:
                    clip1 = clip1.subclip(0, (video_files_start_day[i] - this_start).total_seconds())
                
                if time_difference.total_seconds() > 0:

                    blank_clip = ColorClip(blank_size, blank_color, duration = time_difference.total_seconds())
                    if chunk_starting:
                        merge = concatenate_videoclips([blank_clip, clip2])
                    else:
                        merge = concatenate_videoclips([clip1, blank_clip, clip2])                        
                    
                    del blank_clip
                    
                else:
                    if chunk_starting:
                        merge = clip2
                    else:
                        merge = concatenate_videoclips([clip1, clip2])                        

                if clip1 != None:
                    del clip1
                del clip2

                chunk_starting = False
                pointer += 1
                

            #handle end time
            time_difference = this_end - (this_start + datetime.timedelta(seconds = merge.duration))
            if time_difference.total_seconds() > 0:
                blank_clip = ColorClip(blank_size, blank_color, duration = time_difference.total_seconds())
                merge = concatenate_videoclips([merge, blank_clip])
                del blank_clip

            output_start = this_start.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(local_timezone)).hour
            #output_start = pytz.utc.localize(this_start).astimezone(pytz.timezone(local_timezone)).hour

            output_end = output_start + 1
            print(output_start)
            merge.write_videofile(data_folder.split('/')[1] + '_' + v_folder + '_' + day + '_2hour_' + str(output_start) + '-' + str(output_end) + ".mp4", fps = fps, remove_temp=False)
            merge.close()



