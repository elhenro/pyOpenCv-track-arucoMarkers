import cv2
# import matplotlib 
import numpy as np
import sys
import time

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)

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
