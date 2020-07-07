#!/usr/bin/env python3
import os
import platform
import time

import cv2
import pyrealsense2 as rs
import numpy as np
from cubemos.core.nativewrapper import CM_TargetComputeDevice
from cubemos.core.nativewrapper import initialise_logging, CM_LogLevel
from cubemos.skeleton_tracking.nativewrapper import Api


class CubemosData:
    """
    Creates an object that returns a list of joints in standard format.

    Attributes
    ___________
    image_width: camera resolution
    image_height: camera resolution
    frame: pyrealense2 or opencv frame

    Methods
    _______
    __init__(self, image_width=1280, image_height=720):

    estimate_skeleton(self, frames):

    default_log_dir(self):

    default_license_dir(self):

    check_license_and_variables_exist(self):

    render_result(self, skeletons, img, confidence_threshold):
    """
    def __init__(self, image_width=1280, image_height=720):

        self.check_license_and_variables_exist()

        # Get the path of the native libraries and ressource files
        sdk_path = os.environ["CUBEMOS_SKEL_SDK"]
        initialise_logging(sdk_path, CM_LogLevel.CM_LL_INFO, True, self.default_log_dir())

        # Configure depth and color streams of the intel realsense
        self.image_width = image_width
        self.image_height = image_height

        # Initialize the cubemos api with a valid license key in default_license_dir()
        self.api = Api(self.default_license_dir())
        model_path = os.path.join(
            sdk_path, "models", "skeleton-tracking", "fp32", "skeleton-tracking.cubemos"
        )
        self.api.load_model(CM_TargetComputeDevice.CM_CPU, model_path)

        # Get the intrinsics information for calculation of 3D point
        # frames = pipeline.wait_for_frames()
        # depth = frames.get_depth_frame()
        # depth_intrin = depth.profile.as_video_stream_profile().intrinsics
        #

    def estimate_skeleton(self, frame):
        """
        Returns a dictionary of joint data:
            {
                'number_skeletons': <int>
                skeleton_index = <int>:{
                                    'joints': <list>,
                                    'joints_confidence': <list>,
                                    'human_confidence': <list>
                                    }
            }

        :param frame: opencv or pyrealsense2 frame
        :return: dictionary of the frame data
        """
        try:
            if isinstance(frame, rs.pyrealsense2.composite_frame):
                # frames = pipeline.wait_for_frames()
                depth = frame.get_depth_frame()
                color = frame.get_color_frame()

                # # Convert images to numpy arrays
                depth_image = np.asanyarray(depth.get_data())
                color_image = np.asanyarray(color.get_data())
            else:
                color_image = frame

            # perform inference
            skeletons = self.api.estimate_keypoints(color_image, 256)
            # print("skeletons:", skeletons)

            joint_data = {
                'number_skeletons': len(skeletons)
            }

            # sometimes len(skeletons)==0, does not throw exception when human not detected
            for skeleton_index, skeleton in enumerate(skeletons):
                joints = []
                confidence = skeleton.confidences
                joints_depth = []
                # print(skeleton.joints)
                for joint in skeleton.joints:
                    # build list of normalized data
                    try:
                        joints.append(joint.x / self.image_width)
                        joints.append(joint.y / self.image_height)
                    except Exception as ex:
                        print("Exception occured: \"{}\"".format(ex))


                    # joints_depth.append(depth.get_distance(int(joint.x), int(joint.y)))


                # TODO: check joint index for average
                # append a zero at the end to use as a fill value for other joints
                joints.append((joints[16] + joints[22]) / 2)
                joints.append((joints[23] + joints[17]) / 2)
                joints.append(joints[28] + joints[32] + joints[30] + joints[34] / 4)
                joints.append(joints[29] + joints[33] + joints[31] + joints[35] / 4)

                joints.append(0)

                # TODO: add comments for which joints
                confidence.append(confidence[11] * confidence[8])
                confidence.append(confidence[14] * confidence[15] * confidence[16] * confidence[17])
                confidence.append(0)
                zero = len(joints) - 1
                zero_c = len(confidence) - 1

                new_confidence_index = [10, 9, 8, 11, 12, 13, 18, 1, 1, 19, 4, 3, 2, 5, 6, 7, 0, 14, 16,
                                       15, 17, zero_c, zero_c, zero_c, zero_c]

                new_joint_index = [20, 21, 18, 19, 16, 17, 22, 23, 24, 25, 26, 27, 36, 37,
                                   2, 3, 2, 3, 38, 39, 8, 9, 6, 7, 4, 5, 10, 11, 12, 13, 14, 15,
                                   0, 1, 28, 29, 32, 33, 30, 31, 34, 35, zero, zero, zero, zero, zero, zero, zero, zero]

                new_joints = [joints[i] for i in new_joint_index]
                new_confidence = [confidence[i] for i in new_confidence_index]
                # TODO: update confidence values
                joint_data[str(skeleton_index)] = {'joints': new_joints,
                                                   'joints_confidence': new_confidence,
                                                   'human_confidence': [0] * len(new_joints)
                                                   }

                # TODO: remove print statements
                print(confidence[20])
                print(confidence[19])
                print(confidence[18])
            return joint_data #, self.keypoint_ids

        except Exception as ex:
            print("Exception occured: \"{}\"".format(ex))


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

    def default_log_dir(self):
        if platform.system() == "Windows":
            return os.path.join(os.environ["LOCALAPPDATA"], "Cubemos", "SkeletonTracking", "logs")
        elif platform.system() == "Linux":
            return os.path.join(os.environ["HOME"], ".cubemos", "skeleton_tracking", "logs")
        else:
            raise Exception("{} is not supported".format(platform.system()))

    def default_license_dir(self):
        if platform.system() == "Windows":
            return os.path.join(os.environ["LOCALAPPDATA"], "Cubemos", "SkeletonTracking", "license")
        elif platform.system() == "Linux":
            return os.path.join(os.environ["HOME"], ".cubemos", "skeleton_tracking", "license")
        else:
            raise Exception("{} is not supported".format(platform.system()))

    def check_license_and_variables_exist(self):
        license_path = os.path.join(self.default_license_dir(), "cubemos_license.json")
        if not os.path.isfile(license_path):
            raise Exception(
                "The license file has not been found at location \"" +
                self.default_license_dir() + "\". "
                                             "Please have a look at the Getting Started Guide on how to "
                                             "use the post-installation script to generate the license file")
        if "CUBEMOS_SKEL_SDK" not in os.environ:
            raise Exception(
                "The environment Variable \"CUBEMOS_SKEL_SDK\" is not set. "
                "Please check the troubleshooting section in the Getting "
                "Started Guide to resolve this issue."
            )

    def get_valid_limbs(self, keypoint_ids, skeleton, confidence_threshold):
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

    def render_result(self, skeletons, img, confidence_threshold):
        skeleton_color = (100, 254, 213)
        for index, skeleton in enumerate(skeletons):
            limbs = self.get_valid_limbs(self.keypoint_ids, skeleton, confidence_threshold)
            for limb in limbs:
                cv2.line(
                    img, limb[0], limb[1], skeleton_color, thickness=2, lineType=cv2.LINE_AA
                )
