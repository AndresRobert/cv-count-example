from cvCustomLib.cvDetectionWrapper import ObjectCounter

# define your camera here
USE_GOPRO = 0, 1280, 720
USE_WEBCAM = 1, 640, 480
USE_CUSTOM_VGA = 0, 640, 480
USE_CUSTOM_720p = 0, 1280, 720
USE_CUSTOM_1080p = 0, 1920, 1080
USE_CUSTOM_4k = 0, 3840, 2160

if __name__ == '__main__':  # prevents parts of code from being run when the modules are imported
    object_counter = ObjectCounter(show_detection_camera=True)
    object_counter.count(USE_GOPRO)  # use your camera here
