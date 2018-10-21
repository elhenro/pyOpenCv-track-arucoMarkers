import numpy as np
import cv2
import glob
import sys

calibrationResultImage = "calibration-result.png"

terminationCriteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

objpoints = [] 
imgpoints = [] 

images = glob.glob('calibrate/*.jpg')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find chessboard corners
    ret, corners = cv2.findChessboardCorners(gray, (9,6), None)

    if ret == True:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),terminationCriteria)
        imgpoints.append(corners2)
        img = cv2.drawChessboardCorners(img, (7,6), corners2,ret)

print(objpoints, imgpoints)

#ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

#print( ret, mtx, dist, rvecs, tvecs )
#sys.exit
#img = cv2.imread(calibrateImage)
#h,  w = img.shape[:2]

#newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

# undistort
#mapx,mapy = cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w,h),5)
##dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
#dst = cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR)

#x,y,w,h = roi
#dst = dst[y:y+h, x:x+w]
#cv2.imwrite(calibrationResultImage,dst)
