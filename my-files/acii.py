import pyrealsense2 as rs # Opensource Python wrapper for RealSense SDK 2.0
import numpy as np  # for easy array manipulation
import cv2          # for easy image rendering
import argparse     # for command-line options
import os.path      # for file path manipulation
import sys          # for exception handling
import linecache    # for exception handling

try:
    # Declare RealSense pipeline, encapsulating the actual device and sensors
    pipeline = rs.pipeline()
    pipeline.start()

    # Waits until a new coherent set of frames is available on camera
    while True:
        # Get frameset of depth
        frames = pipeline.wait_for_frames()

        # Get depth frame
        depth_frame = frames.get_depth_frame()
        
        if not depth_frame: continue

        # Print a simple text-based representation of the image, by breaking it into 10x20 pixel regions and approximating the coverage of pixels within one meter
        coverage = [0]*64
        for y in range(480):
            for x in range(640):
                dist = depth_frame.get_distance(x, y)
                if 0 < dist and dist < 1:
                    coverage[x//10] += 1
            
            if y%20 is 19:
                line = ""
                for c in coverage:
                    line += " .:nhBXWW"[c//25]
                coverage = [0]*64
                print(line)
    exit(0)

except Exception:
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print(f'LINE NUMBER: {lineno}   ERROR TYPE: {exc_obj}   EXCEPTION IN FILE: {filename}')

finally:
    pipeline.stop()