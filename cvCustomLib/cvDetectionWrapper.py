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
            out_acceleration_tolerance=10,
            frame_tolerance=100,
            show_detection_camera=False
    ):
        """
        Constructor
        """
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

    def has_crossed_entrance(self, centroid_y):
        """
        Check if an object in entering in monitored zone
        Arguments:
            centroid_y: Integer
        Returns:
            Boolean
        """
        if abs(centroid_y - self.offset_ref_lines) <= self.in_acceleration_tolerance \
                and centroid_y < self.image_height - self.offset_ref_lines:
            return True
        return False

    def has_crossed_exit(self, centroid_y):
        """
        Check if an object in exiting from monitored zone
        Arguments:
            centroid_y: Integer
        Returns:
            Boolean
        """
        if abs(centroid_y - (self.image_height - self.offset_ref_lines)) <= self.out_acceleration_tolerance \
                and centroid_y > self.offset_ref_lines:
            return True
        return False

    def is_too_small(self, detected_object):
        """
        Check if an object meets the minimum area for valid detection
        Arguments:
            detected_object: high contrast frame
        Returns:
            Boolean
        """
        return cv2.contourArea(detected_object) < self.min_object_area

    def is_out_of_bounds(self, centroid_x):
        """
        Check if an object is detected out of the configured detection area
        Arguments:
            centroid_x: Integer
        Returns:
            Boolean
        """
        if centroid_x < self.offset_detection_lines or centroid_x > self.image_width - self.offset_detection_lines:
            return True
        return False

    # Background subtraction and image binarization
    def get_threshold(self, reference_image, current_image):
        """
        Returns a High contrast image detecting the moving object by background subtraction and image binarization
        Arguments:
            reference_image: frame
            current_image: frame
        Returns:
            Boolean
        """
        return cv2.dilate(
            cv2.threshold(  # apply high contrast to movement detected
                cv2.absdiff(  # detect moving object
                    reference_image,
                    Camera.apply_detection_filter(current_image)
                ),
                self.binarization_threshold, 255, cv2.THRESH_BINARY
            )[1],
            None,
            iterations=2
        )

    def detect_moving_objects(self, reference_image, current_image):
        """
        Finds the border and area by the difference between the current image and the reference
        Arguments:
            reference_image: frame
            current_image: frame
        Returns:
            Boolean
        """
        return cv2.findContours(
            self.get_threshold(reference_image, current_image).copy(),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )[0]

    def plot_horizontal_line(self, image, top, color=Rgb.RED, thickness=2):
        """
        Plots a line from left to right
        Arguments:
            image: frame
            top: Integer
            color: Optional. RGB (int b, int g, int r)
            thickness: Optional. Integer
        """
        cv2.line(
            image,
            (0, top),
            (self.image_width, top),
            color,
            thickness
        )

    def plot_vertical_line(self, image, left, color=Rgb.RED, thickness=2):
        """
        Plots a line from top to bottom
        Arguments:
            image: frame
            left: Integer
            color: Optional. RGB (int b, int g, int r)
            thickness: Optional. Integer
        """
        cv2.line(
            image,
            (left, 0),
            (left, self.image_height),
            color,
            thickness
        )

    def plot_reference_lines(self, image):
        """
        Plots reference grid: entrance and exit lines, and detecting area lines
        Arguments:
            image: frame
        """
        self.plot_horizontal_line(image, self.offset_ref_lines, Rgb.BLUE)  # top
        self.plot_horizontal_line(image, self.image_height - self.offset_ref_lines, Rgb.BLUE)  # bottom
        self.plot_vertical_line(image, self.offset_detection_lines, Rgb.GREEN)  # left
        self.plot_vertical_line(image, self.image_width - self.offset_detection_lines, Rgb.GREEN)  # right

    def plot_text(self, image, text, position, color=Rgb.WHITE, font_scale=0.5, thickness=1):
        """
        Plots text
        Arguments:
            image: frame
            text: String
            position: Integer.
            color: Optional. RGB (int b, int g, int r)
            font_scale: Optional. Float
            thickness: Optional. Integer
        """
        cv2.putText(
            image,
            text,
            (self.text_offset_x, position),  # coordinates from top-left corner
            cv2.FONT_HERSHEY_SIMPLEX,  # font
            font_scale,
            color,
            thickness
        )

    def plot_full_grid(self, image, step=10, color=Rgb.GRAY):
        """
        Plots a full grid for measuring debugging
        Arguments:
            image: frame
            step: Optional. Line separation
        """
        i = 0
        while i <= self.image_width:
            self.plot_vertical_line(image, i, color, 1)
            i += step
        i = 0
        while i <= self.image_height:
            self.plot_horizontal_line(image, i, color, 1)
            i += step

    def count(self, camera_setup):
        """
        Plots a full grid for measuring debugging
        Arguments:
            camera_setup: (index, width and height)
        """
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

            if not grabbed:
                Log.error("No frames can be found, check your camera configuration")
                break

            frame = imutils.resize(frame, self.image_width, self.image_height)

            if Camera.is_not_set(reference_frame):
                reference_frame = Camera.apply_detection_filter(frame)
                Log.debug("Reference frame has been set")
                continue

            debug_frame = self.get_threshold(reference_frame, frame)
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
                    Log.info("Current TS: {}ms".format(current_ts))
                    Log.info("Entrance delay: {}ms".format(current_ts - last_in_ts))
                    if current_ts - last_in_ts > self.frame_tolerance:
                        Log.info("Last Entrance TS: {}".format(last_in_ts))
                        entrance_counter += 1
                    else:
                        Log.info("Object entrance ignored by time tolerance")
                    last_in_ts = current_ts

                if self.has_crossed_exit(centroid_y):
                    Log.info("Current TS: {}".format(current_ts))
                    Log.info("Exit delay: {}ms".format(current_ts - last_out_ts))
                    if current_ts - last_out_ts > self.frame_tolerance:
                        Log.info("Last exit TS: {}".format(last_in_ts))
                        exit_counter += 1
                    else:
                        Log.info("Object exit ignored by time tolerance")
                    last_out_ts = current_ts

                if object_count < min(entrance_counter, exit_counter):
                    object_count = min(entrance_counter, exit_counter)
                    (pos_x, pos_y, obj_width, obj_height) = cv2.boundingRect(moving_object)
                    Log.debug("Object {} | size: {} x {}".format(object_count, obj_width, obj_height))

            # self.plot_full_grid(plot_frame, 50)
            self.plot_reference_lines(plot_frame)
            self.plot_text(plot_frame, "Detected: {}".format(object_count), 20)
            self.plot_text(plot_frame, "Entrances: {}".format(entrance_counter), 110)
            self.plot_text(plot_frame, "Exits: {}".format(exit_counter), 255)
            Camera.show(plot_frame)
            if self.show_detection_camera:
                self.plot_full_grid(debug_frame, 10)
                Camera.show(debug_frame, "debugging")

        camera.release()  # cleanup the camera
        cv2.destroyAllWindows()  # close any open windows
