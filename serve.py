#
#
#
## cli USAGE for this script: $ python3 serve.py in.jpg
##                            # python3 [this] [image_in]

import sys
import math
import numpy as np
import json
import asyncio
import cv2
import websockets

outFile = 'out.jpeg'

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
cameraMatrix = np.array([[1.44727245e+04, 0.00000000e+00, 1.38375952e+03], [0.00000000e+00, 1.41444917e+04, 9.80085072e+02],[0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
distCoeffs = np.array([[-0.34844261, 0.26256965, -0.00075911, 0.00117993, -0.2515726]])

def angles_from_rvec(rvec):
    r_mat, _j_ = cv2.Rodrigues(rvec)
    print(r_mat)
    c = math.atan2(r_mat[1][0], r_mat[0][0])
    return math.degrees(c)

if __name__ == '__main__':
    # async def serveCameraData(websocket, path):
    #async def test():
    #    pass
    async def serveCameraData(websocket, path):
        print('someone connected')
        while True:
            file_in = sys.argv[1]
            print('processing: ', file_in)
            frame = cv2.imread(file_in)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            parameters = cv2.aruco.DetectorParameters_create()
            corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)
            print('Markers: ', ids)
            rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, 20, cameraMatrix, distCoeffs)
            for i in range(0, len(ids)):
                frame = cv2.aruco.drawAxis(frame, cameraMatrix, distCoeffs, rvecs[i], tvecs[i], 20)
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            cv2.imwrite(outFile, frame)
            print('rvecs: ', rvecs, ' tvecs: ', tvecs)
            for i, item in enumerate(rvecs):
                marker = {}
                print(ids[i], angles_from_rvec(item), tvecs[i])
                marker['id'] = ids[i].tolist()
                marker['position'] = tvecs[i].tolist()
                marker['rotation'] = angles_from_rvec(item)
                await websocket.send(json.dumps(marker))
            await asyncio.sleep(0.5)
    socketUp = websockets.serve( serveCameraData, port=4200)
    print('running on port: ', 4200)
    asyncio.get_event_loop().run_until_complete(socketUp)
    asyncio.get_event_loop().run_forever()
