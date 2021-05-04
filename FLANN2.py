# 基于FLANN的匹配器(FLANN based Matcher)定位图片
import numpy as np
import cv2
import time
from matplotlib import pyplot as plt
from depth_sensing import *


def FLANN(zed, template, Posipre):
    MIN_MATCH_COUNT = 10  # 设置最低特征点匹配数量为10
    # template = cv2.imread('PKU.png', 0)  # queryImage
    target = GrabImage(zed)
    Posipre = np.array(Posipre).ravel()
    Posipre = Posipre.astype(np.int)
    # print('Posipre[0]', Posipre[0])
    if Posipre[0] != 1104:
        target = target[Posipre[1] - 200:Posipre[1] + 200, Posipre[0] - 200:Posipre[0] + 200]
    # plt.imshow(target, 'gray')
    # plt.show()

    # Initiate SIFT detector创建sift检测器
    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(target, None)
    # 创建设置FLANN匹配
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    # 舍弃大于0.7的匹配
    for m, n in matches:
        if m.distance < 1.4 * n.distance:
            good.append(m)
    if len(good) > MIN_MATCH_COUNT:
        # 获取关键点的坐标
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        # 计算变换矩阵和MASK
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        h, w = template.shape
        # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        cv2.polylines(target, [np.int32(dst)], True, 0, 2, cv2.LINE_AA)
        Posi = np.median(dst, axis=0)
    else:
        print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
        matchesMask = None

    Positemp = np.copy(Posi[0])
    if Posipre[0] != 1104:
        Positemp[0] = Positemp[0] + Posipre[0] - 200
        Positemp[1] = Positemp[1] + Posipre[1] - 200
    X = np.copy(Positemp)
    X[0] = (X[0] - 1476) / 218.3 * 0.5
    X[1] = (X[1] - 500) / 225 * 0.5
    PosiAC = np.append(X, [2.68])
    # print('小车位置', PosiAC)
    print("小车位置 xyz=(%.2f, %.2f, %.2f) m" % (PosiAC[0], PosiAC[1], PosiAC[2]))
    return PosiAC, Positemp


if __name__ == "__main__":
    Posipre = [[1104, 621]]
    point_cloud, zed, res = OpenCamera()

    MIN_MATCH_COUNT = 10  # 设置最低特征点匹配数量为10
    # template1 =  GrabImage(zed)
    template = cv2.imread('PKU.png', 0)  # queryImage
    start = time.time()
    target = GrabImage(zed)
    plt.imshow(target, 'gray')
    Posipre = np.array(Posipre).ravel()
    Posipre.astype(np.int)
    print(Posipre)
    if Posipre[0] != 1104:
       target = target[Posipre[1] - 200:Posipre[1] + 200, Posipre[0] - 200:Posipre[0] + 200]
    # target = target[621-200:621+200, 1104 - 200:1104 + 200]
    plt.imshow(target)
    print("捕获图像 took %.3f sec." % (time.time() - start))
    # target = cv2.imread('lab15.png', 0)  # trainImage
    # Initiate SIFT detector创建sift检测器

    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(template, None)
    start = time.time()
    kp2, des2 = sift.detectAndCompute(target, None)
    print("detectAndCompute took %.3f sec." % (time.time() - start))
    # 创建设置FLANN匹配
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []

    start = time.time()
    # 舍弃大于0.7的匹配
    for m, n in matches:
        if m.distance < 1.4 * n.distance:
            good.append(m)
    if len(good) > MIN_MATCH_COUNT:
        # 获取关键点的坐标
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        # print(dst_pts)
        # X = np.median(dst_pts, axis=0)
        # 计算变换矩阵和MASK
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        h, w = template.shape
        # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        cv2.polylines(target, [np.int32(dst)], True, 0, 2, cv2.LINE_AA)
        Posi = np.median(dst, axis=0)
    else:
        print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
        matchesMask = None
    draw_params = dict(matchColor=(0, 255, 0),
                       singlePointColor=None,
                       matchesMask=matchesMask,
                       flags=2)
    result = cv2.drawMatches(template, kp1, target, kp2, good, None, **draw_params)
    X = np.copy(Posi[0])
    X[0] = (X[0] - 1476) / 218.3 * 0.5
    X[1] = (X[1] - 500) / 225 * 0.5
    PosiAC = np.append(X, [2.68])
    print(PosiAC)
    print("getPixel took %.3f sec." % (time.time() - start))
    plt.imshow(result, 'gray')
    plt.show()

    # print(X)
