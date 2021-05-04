########################################################################
#
# Copyright (c) 2021, STEREOLABS.
#
# All rights reserved.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################

"""
    This sample demonstrates how to capture a live 3D point cloud   
    with the ZED SDK and display the result in an OpenGL window.    
"""

import sys
import ogl_viewer.viewer as gl
import pyzed.sl as sl
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt # plt 用于显示图片
import matplotlib.image as mpimg # mpimg 用于读取图片


def OpenCamera():
    print("grab Depth Sensing image... Press 'Esc' to quit")
    init = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD2K,
                             depth_mode=sl.DEPTH_MODE.ULTRA,
                             coordinate_units=sl.UNIT.METER,
                             coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP)
    zed = sl.Camera()
    status = zed.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    res = sl.Resolution()
    res.width = 2208  # 720
    res.height = 1242  # 404

    point_cloud = sl.Mat(res.width, res.height, sl.MAT_TYPE.F32_C4, sl.MEM.CPU)

    return point_cloud, zed, res


def GrabPointCloud(point_cloud, zed, res):
    # point_cloud, zed = OpenCamera()
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA, sl.MEM.CPU, res)
        # point_cloud.write('C:/Users/user/Desktop/python/b')

def GrabImage(zed):
    # point_cloud, zed = OpenCamera()
    image = sl.Mat()
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        zed.retrieve_image(image, sl.VIEW.LEFT) # Retrieve the left image
        # image.write('C:/Users/user/Desktop/python/b')
    return image.get_data()


def CloseZed(zed):
    zed.close()


def cutZed(point_cloud_np):
    # 切割
    points3Dx = point_cloud_np[:, :, 0]
    points3Dy = point_cloud_np[:, :, 1]
    points3Dz = point_cloud_np[:, :, 2]
    # points3Dx[np.logical_or(points3Dx <= -0.2, points3Dx >= 1.7)] = np.nan  # 东西方向
    # points3Dy[np.logical_or(points3Dy <= -0.6, points3Dy >= 0.8)] = np.nan  # 北南方向
    # points3Dz[np.logical_or(points3Dz <= -2.5, points3Dz >= -2.05)] = np.nan
    points3Dx[np.logical_or(points3Dx <= -0.1, points3Dx >= 1)] = np.nan  # 东西方向
    points3Dy[np.logical_or(points3Dy <= -0.6, points3Dy >= 0.8)] = np.nan  # 北南方向
    points3Dz[np.logical_or(points3Dz <= -2.5, points3Dz >= -0.05)] = np.nan

    size = list(point_cloud_np.shape)
    size[2] = size[2] - 1
    points3D3 = np.zeros(size)

    points3D3[:, :, 0] = points3Dx
    points3D3[:, :, 1] = points3Dy
    points3D3[:, :, 2] = points3Dz

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np.reshape(points3D3, (-1, 3)))
    pcd.remove_non_finite_points()
    # source = o3d.io.read_point_cloud("C:/Users/user/Desktop/python/car.pcd")
    # pcd.paint_uniform_color([1, 0.706, 0])
    # pcd.uniform_down_sample(100000) # 下采样
    # pcd.hidden_point_removal()
    # 滤波
    # cl, ind = pcd.remove_radius_outlier(nb_points=10, radius=0.01)
    # inlier_cloud = pcd.select_by_index(ind)
    # points3D3 = np.array(inlier_cloud.points)
    points3D3  = np.array(pcd.points) #将pcd转为np

    # a = np.isnan(points3D3)
    # a = np.sum(a, 2)
    # a = a < 1
    # points3D4 = np.zeros(size)
    # points3D4[:, :, 0] = points3D3[:, :, 0]
    # points3D4[:, :, 1] = points3D3[:, :, 1]
    # points3D4[:, :, 2] = points3D3[:, :, 2]
    # # points3D4[np.isnan(points3D4)] = 0
    # points3D4X = points3D4[:, :, 0]
    # points3D4Y = points3D4[:, :, 1]
    # points3D4Z = points3D4[:, :, 2]
    Xcar = np.nanmean(np.nanmean(points3D3[:, 0]))
    Ycar = np.nanmean(np.nanmean(points3D3[:, 1]))
    Zcar = np.nanmean(np.nanmean(points3D3[:, 2]))
    if np.isnan(Xcar) or np.isnan(Ycar) or np.isnan(Zcar):
        Posi = [0, 0, 0]
        print('识别失败')
    else:
        Posi = [Xcar, Ycar, Zcar]
    # point = sl.Mat(res.width, res.height, sl.MAT_TYPE.F32_C4, sl.MEM.CPU)
    # yyy = o3d.geometry.PointCloud.PointCloud
    # point.init_mat(points3D3)
    print(Posi)
    # o3d.visualization.draw_geometries([inlier_cloud])

    return Posi


if __name__ == "__main__":
    print("grab Depth Sensing image... Press 'Esc' to quit")
    init = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD2K,
                             depth_mode=sl.DEPTH_MODE.ULTRA,
                             coordinate_units=sl.UNIT.METER,
                             coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP)
    zed = sl.Camera()
    status = zed.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    res = sl.Resolution()
    res.width = 2208  # 720
    res.height = 1242  # 404

    point_cloud = sl.Mat(res.width, res.height, sl.MAT_TYPE.F32_C4, sl.MEM.CPU)
    image = sl.Mat()
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
    #     zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA, sl.MEM.CPU, res)
    #     # point_cloud.write('C:/Users/user/Desktop/python/b')
    #
    # point_cloud_np = point_cloud.get_data()
    # cutZed(point_cloud_np)
        zed.retrieve_image(image, sl.VIEW.RIGHT) # Retrieve the left image
        image.write('C:/Users/user/Desktop/python/d.png')
    plt.imshow(image.get_data())
    zed.close()
