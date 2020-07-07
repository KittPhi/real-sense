# Python Samples for Intel® RealSense™ camera
Author: Kitt Phi
Date: 7/8/2020

## Create Virutual Environment for python3.7:
Install Python3.7
> sudo apt install python3.7

Install Python Virtual Environment and Pip
> sudo apt-get install python3-pip python3.7-venv python3.7-dev

Create Virtual Environment
> python3.7 -m venv venv3.7

Activate Virutal Environment and For every new terminal
> source venv3.7/bin/activate

## Install Python Libraries:
> pip install opencv-python matplotlib numpy pyrealsense2

> sudo apt-get install python3-tk

## Switch VS Code Python Interpreter (venv)
- Ctrl + Shift + p
- Install pylint

## VS Code tips:
#### Testing part of the code:
- Select one or more lines, then press `Shift+Enter` 

# Cubemos Skeletal Tracking
[Install Instructions](https://dev.intelrealsense.com/docs/skeleton-tracking-sdk-installation-guide)
or `GettingStartedGuide_V16_tag2.3.1.docx`

#### cubemos should be installed inside venv

#### Testing cubemos:
> /opt/cubemos/skeleton_tracking/bin/cpp-image

#### Default models, res, license, and logs are in:
> ~/.cubemos/skeleton_tracking/

#### Contains copies of the skeleton-tracking models
> ~/.cubemos/skeleton_tracking/models 
- must stay in default directories.

# VS Code
###  Add .vscode folder > to create `settings.json`

        {
                "python.pythonPath": "venv3.7/bin/python",
                "python.linting.pylintArgs": ["--generate-members"] 
        }

# pyrealsense2 wrapper for RealSense SDK 2
[Follow Install](https://github.com/IntelRealSense/librealsense/tree/master/wrappers/python) 




