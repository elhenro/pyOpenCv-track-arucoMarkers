import numpy as np
import math
import cv2

from picamera.array import PiRGBArray
from picamera import PiCamera

import asyncio
import logging
#import time
import concurrent



RESOLUTION = (1008,1008)
FRAMERATE = 20
WINDOWS_SIZE = 5

DICTIONARY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
CAMERA_MATRIX = np.array([[1.50140443e+03, 0.00000000e+00, 1.29722443e+03],[0.00000000e+00, 1.50325727e+03, 9.46836750e+02],[0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
DIST_COEFFS = np.array([-0.30994886,  0.10550813, -0.00253145,  0.00142907, -0.01049555])

PARAMETERS =  cv2.aruco.DetectorParameters_create()

MARKER_EDGE = 20

def angles_from_rvec(rvec):
    r_mat, _jacobian = cv2.Rodrigues(rvec);
    a = math.atan2(r_mat[2][1], r_mat[2][2])
    b = math.atan2(-r_mat[2][0], math.sqrt(math.pow(r_mat[2][1],2) + math.pow(r_mat[2][2],2)))
    c = math.atan2(r_mat[1][0], r_mat[0][0])
    return [a,b,c];

def calc_bearing(rvec):
    angles = angles_from_rvec(rvec);
    degree_angle =  math.degrees(angles[2]);
    if degree_angle < 0:
        degree_angle = 360 + degree_angle
    return degree_angle;

def find_markers(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, DICTIONARY, parameters=PARAMETERS)
    rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, MARKER_EDGE, CAMERA_MATRIX, DIST_COEFFS)

    result = set()
    if ids is None:
        return result

    for i in range(0, len(ids)):
        id = str(ids[i][0])

        x = tvecs[i][0][0]
        y = tvecs[i][0][1]
        bearing = calc_bearing(rvecs[i][0])
        result.add((id, x,y,bearing))

    return result

class PositioningSystem:
    def __init__(self, on_update):
        self._on_update = on_update
        self._running = False

    def start(self):
        self._running = True
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._capture());
        loop.run_forever()

    def stop(self):
        self._running = False

    async def _capture(self):
        camera = PiCamera()
        camera.resolution = RESOLUTION
        camera.framerate = FRAMERATE

        rawCapture = PiRGBArray(camera, size=RESOLUTION)
        # allow the camera to warmup
        await asyncio.sleep(0.1)

        for capture in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

            if not(self._running):
                break

            # grab an image from the camera
            frame = capture.array
            markers = find_markers(frame)
            for marker in markers:
                await self._on_update(marker)

            rawCapture.truncate(0)

        camera.close()

# Create a limited thread pool.
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

async def track(on_track):
    ps = PositioningSystem(on_track)

    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, ps.start)
    return ps
