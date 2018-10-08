## david
import numpy as np
import math
import cv2

from picamera.array import PiRGBArray
from picamera import PiCamera

import asyncio
import logging
#import time
import concurrent
## us
import traceback
import statistics



file_out = 'out/test5.jpg'
RESOLUTION = (1008,1008)
FRAMERATE = 30
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
    # cv2.imwrite(file_out, frame)
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, DICTIONARY, parameters=PARAMETERS)
    rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, MARKER_EDGE, CAMERA_MATRIX, DIST_COEFFS)

    h,w = frame.shape[:2] # frame - original frame captured from camera
    newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(CAMERA_MATRIX, DIST_COEFFS, (w,h), 1, (w,h))


    ### testing to get the undistorted image
    ### -> fail
    # newcameramtx, roi = cv2.getOptimalNewCameraMatrix(CAMERA_MATRIX, DIST_COEFFS, (w,h), 1, (w,h))
    # dst = cv2.undistort(gray, CAMERA_MATRIX, DIST_COEFFS, None, newcameramtx)
    # x, y, w, h = roi
    # # dst = dst[y:y+h, x:x+w]
    # cv2.imwrite(file_out, dst)

    result = set()
    if ids is None:
        return result

    for i in range(0, len(ids)):
        try:
            id = str(ids[i][0])


            marker = corners[i]

            undistortedMarker = cv2.undistortPoints(marker, CAMERA_MATRIX, DIST_COEFFS, P=newCameraMatrix)
            # print(marker)
            # print("------------")
            # print(undistortedMarker[0][i][0])
            # print(tvecs[i][0][0])
            # print(undistortedMarker[0][i])
            # print(undistortedMarker[0])


            x1 = marker[0][0][0]
            x2 = marker[0][2][0]
            y1 = marker[0][0][1]
            y2 = marker[0][2][1]
            xCenter = (x1 + x2)/2
            yCenter = (y1 + y2)/2


            # print("Original %s:" % ids[i][0])
            # print(marker)
            #
            # print('Undistorted %s:' % ids[i][0])
            # print(undistortedMarker)

            # x = tvecs[i][0][0]
            # y = tvecs[i][0][1]
            x = xCenter
            y = yCenter
            bearing = calc_bearing(rvecs[i][0])
            result.add((id, x,y,bearing))
        except Exception:
            traceback.print_exc()
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
        watchMarker = {}
        rawCapture = PiRGBArray(camera, size=RESOLUTION)
        # allow the camera to warmup
        await asyncio.sleep(0.1)

        for capture in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

            if not(self._running):
                break

            # grab an image from the camera
            frame = capture.array
            # xMediaMarkers = []
            # yMediaMarkers = []
            # bMediaMarkers = []

            markers = find_markers(frame)
            for marker in markers:
                try:
                    # if marker[0] not in watchMarker:
                    #
                    # watchMarker[marker[0]] = [[[marker[1]],[marker[2]], [marker[3]]]]
                    # # print(watchMarker)
                    # for key in watchMarker.keys():
                    #     if marker[0] == key:
                    #         watchMarker[key[0]].append(marker[1])
                    #         watchMarker[key[1]].append(marker[2])
                    #         watchMarker[key[2]].append(marker[3])
                    #
                    #     if len(key) > 3:
                    #         newX = statistics.median(key[0])
                    #         newY = statistics.median(key[1])
                    #         newB = statistics.median(key[2])
                    #
                    #         ## recreate marker
                    #         #medianMarker = [[]]
                    #
                    #         ## reset key
                    #         watchMarker[key] = []
                    #         # print(newX,  newY, newB)
                    #         # xMediaMarkers = []
                    #         # yMediaMarkers = []
                    #         # bMediaMarkers = []
                    #
                    #         # print(marker)
                    #
                    #         await self._on_update(marker)
                    await self._on_update(marker)

                except Exception:
                    traceback.print_exc()


            rawCapture.truncate(0)
        camera.close()

# Create a limited thread pool.
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

async def track(on_track):
    ps = PositioningSystem(on_track)

    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, ps.start)
    return ps
