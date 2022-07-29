# Object Counter
Simple object counter between 2 lines

## Required Libs
- cv2: `pip3 install OpenCV-Python`
- imutils: `pip3 install imutils`
- time

## Setup

```python
from cvCustomLib.cvDetectionWrapper import ObjectCounter

object_counter_instance = ObjectCounter(
    min_object_area=10,  # minimum object area in squared pixels
    binarization_threshold=30,  # smoothness (the lower, the more moving objects it detects)
    offset_ref_lines=120,  # entrance and exit offset for object detection
    offset_detection_lines=250,  # left and right margin for object detection
    text_offset_x=10,  # text padding from left
    initial_skipped_frames=20,  # expecting initial camera light adjustment
    image_width=640,  # forced image width
    image_height=360,  # forced image height
    in_acceleration_tolerance=6,  # tolerance for object acceleration and camera's frame rate in pixels for entrance
    out_acceleration_tolerance=6,  # tolerance for object acceleration and camera's frame rate in pixels for exit
    frame_tolerance=100,  # a 30fps camera, will get a frame every 30ms; 90ms will wait 3 frames before counting the next passing through object
    show_detection_camera=False  # also show the debug camera to check the detection process
)
```

## Example

```python
from cvCustomLib.cvDetectionWrapper import ObjectCounter

# camera index, width and height
USE_WEBCAM = 0, 640, 480

if __name__ == '__main__':
    # objects = ObjectCounter()  # use default values or
    objects = ObjectCounter(show_detection_camera=True)  # activate the detection camera to debug the binarization_threshold and min_object_area
    objects.count(USE_WEBCAM)

```

![debugging gif](cvCustomLib/img/debug.gif)

As you can see the detection tool in the debugging window will show the actual filter that enables the camera to detect the moving object

## Configuration

### Logging
Set the Log level here:

```python
# cvCustomLib/cvHelpers/cvLogHelper.py#L25
LOG_LEVEL = "DEBUG"  # can be INFO for full frame logging or ERROR for error only logging
```

## Issues
- If the base configuration changes it will detect that as a concurrent movement
- If 2 objects are passing through at the exact same time or in between the `frame_tolerance` time it will only count one of them