import pyrealsense2 as rs

# connect to realsense camera
pipeline = rs.pipeline()
pipeline.start()

try:
    while True:
        # configures pipleline to stream camera
        frames =pipeline.wait_for_frames()

finally:
    pipeline.stop()
