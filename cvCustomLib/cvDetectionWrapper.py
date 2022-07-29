import cv2
import imutils
import time
import cvCustomLib.cvLogHelper as Log
import cvCustomLib.cvCameraHelper as Camera
import cvCustomLib.cvRgbHelper as Rgb


class ObjectCounter:
    def __init__(
            self,
            min_object_area=10,
            binarization_threshold=30,
            offset_ref_lines=120,
            offset_detection_lines=250,
            text_offset_x=10,
            initial_skipped_frames=20,
            image_width=640,
            image_height=360,
            in_acceleration_tolerance=6,
            out_acceleration_tolerance=6,
            frame_tolerance=100,
            show_detection_camera=False
    ):
        self.min_object_area = min_object_area
        self.binarization_threshold = binarization_threshold
        self.offset_ref_lines = offset_ref_lines
        self.offset_detection_lines = offset_detection_lines
        self.text_offset_x = text_offset_x
        self.initial_skipped_frames = initial_skipped_frames
        self.image_width = image_width
        self.image_height = image_height
        self.in_acceleration_tolerance = in_acceleration_tolerance
        self.out_acceleration_tolerance = out_acceleration_tolerance
        self.frame_tolerance = frame_tolerance
        self.show_detection_camera = show_detection_camera

    # Check if an object in entering in monitored zone
    def has_crossed_entrance(self, centroid_y):
        if abs(centroid_y - self.offset_ref_lines) <= self.in_acceleration_tolerance \
                and centroid_y < self.image_height - self.offset_ref_lines:
            return True
        return False

    # Check if an object in exiting from monitored zone
    def has_crossed_exit(self, centroid_y):
        if abs(centroid_y - (self.image_height - self.offset_ref_lines)) <= self.out_acceleration_tolerance \
                and centroid_y > self.offset_ref_lines:
            return True
        return False

    def is_too_small(self, detected_object):
        return cv2.contourArea(detected_object) < self.min_object_area

    # Background subtraction and image binarization
    def get_threshold(self, previous_frame, current_frame):
        return cv2.dilate(
            cv2.threshold(  # apply high contrast to movement detected
                cv2.absdiff(  # detect moving object
                    previous_frame,
                    Camera.apply_detection_filter(current_frame)
                ),
                self.binarization_threshold, 255, cv2.THRESH_BINARY
            )[1],
            None,
            iterations=2
        )

    def detect_moving_objects(self, previous_frame, current_frame):
        return cv2.findContours(
            self.get_threshold(previous_frame, current_frame).copy(),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )[0]

    def plot_horizontal_line(self, image, top, color=Rgb.RED, thickness=2):
        cv2.line(
            image,
            (0, top),
            (self.image_width, top),
            color,
            thickness
        )

    def plot_vertical_line(self, image, left, color=Rgb.RED, thickness=2):
        cv2.line(
            image,
            (left, 0),
            (left, self.image_height),
            color,
            thickness
        )

    # plot entrance and exit lines
    def plot_reference_lines(self, image):
        self.plot_horizontal_line(image, self.offset_ref_lines, Rgb.BLUE)  # top
        self.plot_horizontal_line(image, self.image_height - self.offset_ref_lines, Rgb.BLUE)  # bottom
        self.plot_vertical_line(image, self.offset_detection_lines, Rgb.GREEN)  # left
        self.plot_vertical_line(image, self.image_width - self.offset_detection_lines, Rgb.GREEN)  # right

    def plot_text(self, image, text, position, color=Rgb.WHITE, font_scale=0.5, thickness=1):
        cv2.putText(
            image,
            text,
            (self.text_offset_x, position),  # coordinates from top-left corner
            cv2.FONT_HERSHEY_SIMPLEX,  # font
            font_scale,
            color,
            thickness
        )

    def is_out_of_bounds(self, centroid_x):
        if centroid_x < self.offset_detection_lines or centroid_x > self.image_width - self.offset_detection_lines:
            return True
        return False

    def plot_full_grid(self, image, step=10):
        i = 0
        while i <= self.image_width:
            self.plot_vertical_line(image, i, Rgb.GRAY, 1)
            i += step
        i = 0
        while i <= self.image_height:
            self.plot_horizontal_line(image, i, Rgb.GRAY, 1)
            i += step

    def count(self, camera_setup):
        camera = Camera.get_camera(camera_setup)
        Log.debug("Camera is set to {} x {} resolution".format(camera_setup[1], camera_setup[2]))
        Camera.skip_frames(camera, self.initial_skipped_frames)
        Log.info("{} frames have been skipped".format(self.initial_skipped_frames))
        reference_frame = None

        object_count = 0
        entrance_counter = 0
        exit_counter = 0
        last_in_ts = 0
        last_out_ts = 0

        while True:
            (grabbed, frame) = camera.read()
            frame = imutils.resize(frame, self.image_width, self.image_height)

            if not grabbed:
                Log.error("No frames can be found, check your camera configuration")
                break

            if Camera.is_not_set(reference_frame):
                reference_frame = Camera.apply_detection_filter(frame)
                Log.debug("Reference frame has been set")
                continue

            plot_frame = frame.copy()
            for moving_object in self.detect_moving_objects(reference_frame, frame):
                if self.is_too_small(moving_object):
                    Log.info("Object detected is too small, hence ignored")
                    continue

                centroid_x, centroid_y = Camera.get_centroid(moving_object)
                if self.is_out_of_bounds(centroid_x):
                    Log.info("Object is out of bounds, hence ignored")
                    continue

                Log.info("Valid object detected")
                Camera.plot_object_box(plot_frame, moving_object, Rgb.GREEN)
                current_ts = int(time.time() * 100)

                if self.has_crossed_entrance(centroid_y):
                    Log.info("Current TS: {}".format(current_ts))
                    Log.debug("IN Delay: {}ms".format(current_ts - last_in_ts))
                    if current_ts - last_in_ts > self.frame_tolerance:
                        Log.info("Last IN TS: {}".format(last_in_ts))
                        entrance_counter += 1
                    last_in_ts = current_ts

                if self.has_crossed_exit(centroid_y):
                    Log.info("Current TS: {}".format(current_ts))
                    Log.debug("OUT Delay: {}ms".format(current_ts - last_out_ts))
                    if current_ts - last_out_ts > self.frame_tolerance:
                        Log.info("Last OUT TS: {}".format(last_in_ts))
                        exit_counter += 1
                    last_out_ts = current_ts

                object_count = min(entrance_counter, exit_counter)

            # plot_full_grid(plot_frame, 50)
            self.plot_reference_lines(plot_frame)
            self.plot_text(plot_frame, "Detected: {}".format(object_count), 20)
            self.plot_text(plot_frame, "Entrances: {}".format(entrance_counter), 110)
            self.plot_text(plot_frame, "Exits: {}".format(exit_counter), 255)
            Camera.show(plot_frame)
            if self.show_detection_camera:
                Camera.show(self.get_threshold(reference_frame, frame), "debugging")

        camera.release()  # cleanup the camera
        cv2.destroyAllWindows()  # close any open windows
