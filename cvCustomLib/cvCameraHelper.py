import cv2
import cvCustomLib.cvRgbHelper as Rgb


def is_not_set(image):
    """
    Checks if an image is not defined
    Arguments:
        image: captured frame instance
    Returns:
        Boolean
    """
    return image is None


def get_camera(source):
    """
    Starts a new VideoCapture instance from cv2 library
    Arguments:
        source: (index, width and height)
    Returns:
        VideoCapture instance
    """
    source_index, source_width, source_height = source
    camera = cv2.VideoCapture(source_index)
    camera.set(3, source_width)
    camera.set(4, source_height)
    return camera


def get_centroid(detected_object):
    """
    Get the bounding rectangle on the detected object and calculates the centroid [(x1 + x2)/2, (y1 + y2)/2]
    Arguments:
        detected_object: high contrast frame
    Returns:
        centroid (int x, int y)
    """
    (pos_x, pos_y, obj_width, obj_height) = cv2.boundingRect(detected_object)
    return int((pos_x + pos_x + obj_width) / 2), int((pos_y + pos_y + obj_height) / 2)


def skip_frames(camera, number_of_frames):
    """
    When a camera is starting it adjusts light. Skipping some initial frames will improve the reference frame accuracy for moving object detection
    Arguments:
        camera: CaptureVideo instance object
        number_of_frames: positive integer
    """
    for i in range(0, number_of_frames):
        camera.read()


def apply_detection_filter(image):
    """
    Applies gray-scale conversion and gaussian blur filter for object smoothing
    Arguments:
        image: captured frame
    Returns:
        filtered image
    """
    return cv2.GaussianBlur(
        cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY  # color filter
        ),
        (21, 21),  # standard deviation for x and y smoothness
        0,  # sigma x
        0  # sigma y
    )


def plot_bounding_rectangle(image, start, end, color=Rgb.GREEN, thickness=2):
    """
    Plots the bounding rectangle on the detected object
    Arguments:
        image: captured frame
        start: (int x, int y)
        end: (int x, int y)
        color: Optional. RGB (int blue, int green, int red)
        thickness: Optional. Integer
    """
    cv2.rectangle(
        image,
        start,
        end,
        color,
        thickness
    )


def plot_inner_centroid(image, centroid, color=Rgb.GREEN, thickness=3):
    """
    Plots the centroid in the detected object
    Arguments:
        image: captured frame
        centroid: (int x, int y)
        color: Optional. RGB (int blue, int green, int red)
        thickness: Optional. Integer. it's used also for plotting radius
    """
    cv2.circle(
        image,
        centroid,
        radius=thickness,
        color=color,
        thickness=thickness
    )


def plot_object_box(image, detected_object, color=Rgb.GREEN):
    """
    Plots full object identification: bounding rectangle and centroid
    Arguments:
        image: captured frame
        detected_object: high contrast frame
        color: Optional. RGB (int blue, int green, int red)
    """
    (pos_x, pos_y, obj_width, obj_height) = cv2.boundingRect(detected_object)
    plot_bounding_rectangle(
        image,
        (pos_x, pos_y),
        (pos_x + obj_width, pos_y + obj_height),
        color
    )
    plot_inner_centroid(
        image,
        (int((pos_x + pos_x + obj_width) / 2), int((pos_y + pos_y + obj_height) / 2)),
        color
    )


def show(image, title="camera"):
    """
    Opens a video window with specific frames and title
    Arguments:
        image: captured frame
        title: Optional. String
    """
    cv2.imshow(title, image)
    cv2.waitKey(1)
