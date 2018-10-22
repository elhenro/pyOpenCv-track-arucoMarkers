import numpy as np
import cv2 as cv
import glob

print('running');
# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*9,3), np.float32)
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('calibrate/*.jpeg')

#images = glob.glob('calib2/cam12.jpg')
images.extend(glob.glob('calibrate/chess_big_*.jpg'))
#images.extend(glob.glob('calib2/cam12.jpg'))
#images = glob.glob('calib2/chess_big_*.jpg')

i = 0
for fname in images:
    print(fname);

    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (9,6), None)
    #cv.imwrite('test_x' + str(i) + '.png', gray)
    i += 1
    # If found, add object points, image points (after refining them)
    print(ret);
    if ret == True:

        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)
        # Draw and display the corners
        imgWithCorners = img.copy()
        cv.drawChessboardCorners(imgWithCorners, (9,6), corners2, ret)
        cv.imwrite('test2_corners_' + str(i) + '.jpeg', imgWithCorners)


ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print(mtx)
print('')
print(dist)

img = cv.imread('in.jpg')

h,  w = img.shape[:2]
print(h,w)
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

dst = cv.undistort(img, mtx, dist, None, newcameramtx)
# crop the image

x, y, w, h = roi
print(x,y,w,h)

dst = dst[y:y+h, x:x+w]
cv.imwrite('out_undistorted.jpeg', dst)