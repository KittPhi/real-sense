# Opensource Python wrapper for RealSense SDK 2.0
import pyrealsense2 as rs

import numpy as np
import cv2

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)


