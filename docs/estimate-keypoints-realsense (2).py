#!/usr/bin/env python3
import json
import os
import platform
import time
from collections import namedtuple

import cv2
import numpy as np
import pyrealsense2 as rs
from cubemos.core.nativewrapper import CM_TargetComputeDevice
from cubemos.core.nativewrapper import initialise_logging, CM_LogLevel
from cubemos.skeleton_tracking.nativewrapper import Api

keypoint_ids = [
    (1, 2),
    (1, 5),
    (2, 3),
    (3, 4),
    (5, 6),
    (6, 7),
    (1, 8),
    (8, 9),
    (9, 10),
    (1, 11),
    (11, 12),
    (12, 13),
    (1, 0),
    (0, 14),
    (14, 16),
    (0, 15),
    (15, 17),
]


def default_log_dir():
    if platform.system() == "Windows":
        return os.path.join(os.environ["LOCALAPPDATA"], "Cubemos", "SkeletonTracking", "logs")
    elif platform.system() == "Linux":
        return os.path.join(os.environ["HOME"], ".cubemos", "skeleton_tracking", "logs")
    else:
        raise Exception("{} is not supported".format(platform.system()))


def default_license_dir():
    if platform.system() == "Windows":
        return os.path.join(os.environ["LOCALAPPDATA"], "Cubemos", "SkeletonTracking", "license")
    elif platform.system() == "Linux":
        return os.path.join(os.environ["HOME"], ".cubemos", "skeleton_tracking", "license")
    else:
        raise Exception("{} is not supported".format(platform.system()))


def check_license_and_variables_exist():
    license_path = os.path.join(default_license_dir(), "cubemos_license.json")
    if not os.path.isfile(license_path):
        raise Exception(
            "The license file has not been found at location \"" +
            default_license_dir() + "\". "
            "Please have a look at the Getting Started Guide on how to "
            "use the post-installation script to generate the license file")
    if "CUBEMOS_SKEL_SDK" not in os.environ:
        raise Exception(
            "The environment Variable \"CUBEMOS_SKEL_SDK\" is not set. "
            "Please check the troubleshooting section in the Getting "
            "Started Guide to resolve this issue." 
        )


def get_valid_limbs(keypoint_ids, skeleton, confidence_threshold):
    limbs = [
        (tuple(map(int, skeleton.joints[i])), tuple(map(int, skeleton.joints[v])))
        for (i, v) in keypoint_ids
        if skeleton.confidences[i] >= confidence_threshold
        and skeleton.confidences[v] >= confidence_threshold
    ]
    valid_limbs = [
        limb
        for limb in limbs
        if limb[0][0] >= 0 and limb[0][1] >= 0 and limb[1][0] >= 0 and limb[1][1] >= 0
    ]
    return valid_limbs


def render_result(skeletons, img, confidence_threshold):
    skeleton_color = (100, 254, 213)
    for index, skeleton in enumerate(skeletons):
        limbs = get_valid_limbs(keypoint_ids, skeleton, confidence_threshold)
        for limb in limbs:
            cv2.line(
                img, limb[0], limb[1], skeleton_color, thickness=2, lineType=cv2.LINE_AA
            )


# Main content begins
if __name__ == "__main__":
    try:
        check_license_and_variables_exist()

        # Get the path of the native libraries and ressource files
        sdk_path = os.environ["CUBEMOS_SKEL_SDK"]
        initialise_logging(sdk_path, CM_LogLevel.CM_LL_INFO, True, default_log_dir())

        # Configure depth and color streams of the intel realsense
        image_width = 1280
        image_height = 720

        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, image_width, image_height, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, image_width, image_height, rs.format.bgr8, 30)

        pipeline = rs.pipeline()
        pipeline.start()

        # Initialize the cubemos api with a valid license key in default_license_dir()
        api = Api(default_license_dir())
        model_path = os.path.join(
            sdk_path, "models", "skeleton-tracking", "fp32", "skeleton-tracking.cubemos"
        )
        api.load_model(CM_TargetComputeDevice.CM_CPU, model_path)

        # Tuple object to push the calculated 3D skeleton data to 
        skeletons_3D = namedtuple("skeletons_3D", ["id", "joints"])

        # Information on saving the skeletons
        print("Press 's' to save the skeletons tracked in a frame to a JSON file.")

        # Get the intrinsics information for calculation of 3D point
        frames = pipeline.wait_for_frames()
        depth = frames.get_depth_frame()
        depth_intrin = depth.profile.as_video_stream_profile().intrinsics

        all_joints = {}
        all_joints_depth = {}

        try:
            while True:
                # Create a pipeline object. This object configures the streaming camera and owns it's handle
                frames = pipeline.wait_for_frames()
                depth = frames.get_depth_frame()
                color = frames.get_color_frame()
                if not depth or not color: continue

                # Convert images to numpy arrays
                depth_image = np.asanyarray(depth.get_data())
                color_image = np.asanyarray(color.get_data())

                frame_time = time.time()

                print("<"*15, frame_time, ">"*15)
                #perform inference
                skeletons = api.estimate_keypoints(color_image, 256)
                # print("skeletons:", skeletons)

                # sometimes len(skeletons)==0, does not throw exception when human not detected
                if len(skeletons) > 0:
                    skeleton = skeletons[0]
                    joints = []
                    joints_depth = []
                    print(skeleton.joints)
                    for joint in skeleton.joints:
                        # build list of normalized data
                        joints.append(joint.x/image_width)
                        joints.append(joint.y/image_height)
                        # joints_depth.append(depth.get_distance(int(joint.x), int(joint.y)))

                    print(joints)
                    print(joints_depth)
                    all_joints[frame_time] = joints
                    all_joints_depth[frame_time] = joints_depth
                else:
                    all_joints[frame_time] = [0]
                    all_joints_depth[frame_time] = [0]

                print("*" * 50)
                # *****************************************************************
                # I don't think this is needed
                #
                # perform inference again to demonstrate tracking functionality.
                # usually you would estimate the keypoints on another image and then
                # update the tracking id
                # new_skeletons = api.estimate_keypoints(color_image, 256)
                # print("new_skeletons:", new_skeletons)
                # new_skeletons = api.update_tracking_id(skeletons, new_skeletons)
                # print("new_skeletons:", new_skeletons)
                # print("skeletons:", skeletons)
                # print("*"*50)
                # *********************************************************************

                # render the skeletons on top of the acquired image and display it
                color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB) #color adjustment, not sure what is going on
                render_result(skeletons, color_image, 0.5)
                cv2.namedWindow('cubemos skeleton tracking', cv2.WINDOW_AUTOSIZE)
                cv2.imshow('cubemos skeleton tracking', color_image)

                keyPressed = cv2.waitKey(1)
                if keyPressed == 115:
                    skeleton_dump = []
                    data_filename = 'data-' +  time.strftime("%Y%m%d-%H%M%S") + '.json'
                    # calculate 3D keypoints if the trigger with the keyboard was made
                    with open(data_filename, 'w') as outfile:
                        for skeleton_index in range(len(skeletons)):
                            skeleton_2D = skeletons[skeleton_index]
                            joints_2D = skeleton_2D.joints
                            joints_3D = [[-1,-1,-1]] *  len(joints_2D) 
                            for joint_index in range(len(joints_2D)):                        
                                # check if the joint was detected and has valid coordinate
                                # if so, calculate 3d point based on it and write it to the json dump
                                if skeleton_2D.confidences[joint_index] > 0.01 :

                                    # if the image co-ordinate is beyond the width of the image, correct it
                                    if joints_2D[joint_index].x >= image_width:
                                        joints_2D[joint_index].x = image_width - 1
                                    if joints_2D[joint_index].y >= image_height:
                                        joints_2D[joint_index].y = image_height - 1 

                                    distance = depth.get_distance(int(joints_2D[joint_index].x), int(joints_2D[joint_index].y))
                                    depth_pixel = [ int(joints_2D[joint_index].x), int(joints_2D[joint_index].y)]
                                    if distance >= 0.3:
                                        point_3d = rs.rs2_deproject_pixel_to_point(depth_intrin, depth_pixel, distance)
                                        joints_3D[joint_index] = point_3d
                            skeleton_dump.append(skeletons_3D(skeleton_2D.id, joints_3D))
                        # write the calculated keypoints for all the skeletons into a JSON file
                        json.dump(skeleton_dump, outfile)
                        print("Saved the skeletons to the file " + data_filename)
                elif keyPressed == 113:
                    print(all_joints)
                    print(all_joints_depth)
                    break
 
        finally:
            pipeline.stop()
            
    except Exception as ex:
        print("Exception occured: \"{}\"".format(ex))
