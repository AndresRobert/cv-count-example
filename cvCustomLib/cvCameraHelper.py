import cv2
import cvCustomLib.cvRgbHelper as Rgb


def is_not_set(image):
    return image is None


def get_camera(source):
    source_index, source_width, source_height = source
    camera = cv2.VideoCapture(source_index)
    camera.set(3, source_width)
    camera.set(4, source_height)
    return camera


def get_centroid(moving_object):
    (pos_x, pos_y, obj_width, obj_height) = cv2.boundingRect(moving_object)
    return int((pos_x + pos_x + obj_width) / 2), int((pos_y + pos_y + obj_height) / 2)


def skip_frames(camera, number_of_frames):
    for i in range(0, number_of_frames):
        camera.read()


# gray-scale conversion and Gaussian blur filter applying
def apply_detection_filter(image):
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
    cv2.rectangle(
        image,
        start,
        end,
        color,
        thickness
    )


def plot_inner_centroid(image, centroid, color=Rgb.GREEN, thickness=3):
    cv2.circle(
        image,
        centroid,
        radius=thickness,
        color=color,
        thickness=thickness
    )


def plot_object_box(frame, moving_object, color=Rgb.GREEN):
    (pos_x, pos_y, obj_width, obj_height) = cv2.boundingRect(moving_object)
    plot_bounding_rectangle(
        frame,
        (pos_x, pos_y),
        (pos_x + obj_width, pos_y + obj_height),
        color
    )
    plot_inner_centroid(
        frame,
        (int((pos_x + pos_x + obj_width) / 2), int((pos_y + pos_y + obj_height) / 2)),
        color
    )


def show(image, title="camera"):
    cv2.imshow(title, image)
    cv2.waitKey(1)
