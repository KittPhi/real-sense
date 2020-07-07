# Python realSense OpenCV
## Create virtual environment for python3.7:
- sudo apt install python3.7 python3.7-dev python3.7-venv
- python3.7 -m venv venv3.7
- source venv3.7/bin/activate

## Inside VS Code, switch python interpreter (venv)
- ctrl+shift+p
- install pylint

## VS Code tips:
Select one or more lines, then press Shift+Enter 
- This command is convenient for testing just a part of a file.

pip install opencv-python matplotlib numpy pyrealsense2
sudo apt-get install python3-tk

# Cubemos Skeletal Tracking Install:
# GettingStartedGuide_V16_tag2.3.1.docx
# OTHER: https://dev.intelrealsense.com/docs/skeleton-tracking-sdk-installation-guide
cp /media/kphi/lab-ssd/STUFF/cubemos-SkeletonTracking_2.3.1.6cffde4.deb ~/Downloads && cd ~/Downloads
sudo apt-get install ./cubemos-SkeletonTracking_*.deb # OR
sudo apt-get install ./cubemos-SkeletonTracking_2.3.1.6cffde4.deb
reboot
cd /opt/cubemos/skeleton_tracking/scripts/ && bash post_installation.sh 

# I added this:
pip install /opt/cubemos/skeleton_tracking/wrappers/python/cubemos_core-2.2.1-py3-none-any.whl
pip install /opt/cubemos/skeleton_tracking/wrappers/python/cubemos_skel-2.3.1-py3-none-any.whl

# run test: (If it doensn't work, setup venv and install cubemos in it)
/opt/cubemos/skeleton_tracking/bin/cpp-image

# Install and create Virtual Environment:
sudo apt-get install python3-pip python3.7-venv
python3.7 –m venv ~/cubemos-samples/cube-venv
source ~/cubemos-samples/cube-venv/bin/activate

# Required: Fixes vscode errors "unable to import cubemos,pyrealsense2 and numpy"
pip install pyrealsense2
pip install numpy
pip install --find-links="$CUBEMOS_SKEL_SDK/wrappers/python" --no-index cubemos-core cubemos-skel
cd "$CUBEMOS_SKEL_SDK/samples/python/" 

pip install -r requirements.txt

python estimate-keypoints.py -o ~/output.jpg \
../res/images/skeleton_estimation.jpg

# /opt/cubemos/skeleton_tracking
# "$CUBEMOS_SKEL_SDK"

cd /opt/cubemos/skeleton_tracking/docs/doc_doxygen/html
google-chrome index.html

# Default models, res, license, and logs are in:
~/.cubemos/skeleton_tracking/
/models # contains copies of the skeleton-tracking models
        # >>> must stay in default directories.

