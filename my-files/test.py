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

    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    
    pipeline.start(config)

    # Create opencv window to render image in
    cv2.namedWindow("Depth Stream", cv2.WINDOW_AUTOSIZE)

    # Create colorizer object
    colorizer = rs.colorizer()

    # Waits until a new coherent set of frames is available on camera
    while True:
        # Get frameset of depth
        frames = pipeline.wait_for_frames()

        # Librealsense frames support the buffer protocol. A numpy array 
        # can be constructed using this protocol with no data marshalling
        # overhead:

        # Get depth frame
        depth_frame = frames.get_depth_frame()
        depth_data = depth_frame.as_frame().get_data()
        np_image = np.asanyarray(depth_data)
        print(np_image)

        # Colorize depth frame to jet colormap
        depth_color_frame = colorizer.colorize(depth_frame)

        # Convert depth_frame to numpy array to render image in opencv
        depth_color_image = np.asanyarray(depth_color_frame.get_data())

        # Render image in opencv window
        cv2.imshow("Depth Stream", depth_color_image)

        key = cv2.waitKey(1) # for controlling opencv window
        # if esc is pressed program exits
        if key == 27:
            cv2.destroyAllWindows()
            break

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