import cv2
# import matplotlib 
import numpy as np
import sys
import time

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)

cameraMatrix = np.array([[1.44727245e+04, 0.00000000e+00, 1.38375952e+03], [0.00000000e+00, 1.41444917e+04, 9.80085072e+02], [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
distCoeffs = np.array([[-3.10170732e+01,  1.28689997e+03, -2.42244530e-02, -3.04740368e-02, -2.14942436e+04]])

if __name__ == "__main__":

    try:
        file = sys.argv[1]
    except IndexError:
        file = "in.jpg"
        print('warn: no input file: falling back to file: in.jpg')

    try: 
        out_file = sys.argv[2]
    except IndexError:
        out_file = "out.jpg"
        print('warn: no output file: falling back to file: out.jpg')

    #read
    frame = cv2.imread(file)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    parameters = cv2.aruco.DetectorParameters_create()

    start_time = time.time()

    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)

    frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids, (0, 255, 0))

    cv2.imwrite(out_file, frame)

    print("ran in: %s seconds" % (time.time() - start_time))

rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, 2, cameraMatrix, distCoeffs)

for i in range(0, len(ids)):
    frame = cv2.aruco.drawAxis(frame, cameraMatrix, distCoeffs, rvecs[i], tvecs[i], 2);
    print(rvecs[i])
    print(tvecs[i])
    cv2.imwrite(out_file, frame)

