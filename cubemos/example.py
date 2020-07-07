
import cv2
import numpy as np
import pyrealsense2 as rs
from cubemos_data import CubemosData

# *************************************************************************
# create cubemos object
cubemos = CubemosData()
# *************************************************************************

image_width = 1280
image_height = 720

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, image_width, image_height, rs.format.z16, 30)
config.enable_stream(rs.stream.color, image_width, image_height, rs.format.bgr8, 30)

pipeline = rs.pipeline()
pipeline.start()

frames = pipeline.wait_for_frames()
depth = frames.get_depth_frame()
depth_intrin = depth.profile.as_video_stream_profile().intrinsics
print('press \'q\' to quit.')
while True:
    # Create a pipeline object. This object configures the streaming camera and owns it's handle
    frames = pipeline.wait_for_frames()
    depth = frames.get_depth_frame()
    color = frames.get_color_frame()
    if not depth or not color: continue

    # Convert images to numpy arrays
    depth_image = np.asanyarray(depth.get_data())
    color_image = np.asanyarray(color.get_data())

    color_image = cv2.cvtColor(color_image,
                               cv2.COLOR_BGR2RGB)  # color adjustment, not sure what is going on
    # self.render_result(skeletons, color_image, 0.5)

    # *************************************************************************
    # print the frames, returned as list
    print('press \'q\' to quit.')
    print(cubemos.estimate_skeleton(frames))
    # *************************************************************************

    cv2.namedWindow('cubemos skeleton tracking', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('cubemos skeleton tracking', color_image)

    keyPressed = cv2.waitKey(1)
    if keyPressed == 113:
        break