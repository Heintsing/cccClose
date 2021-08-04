# from matplotlib import pyplot as plt
import numpy as np
#
#
# Pattern = np.ones([24, 24])
#
#
# fig = plt.figure()
# plt.pcolor(Pattern, cmap='jet', edgecolors='k', linewidths=0.4)
# plt.colorbar(shrink=.83)
# plt.xticks()
# plt.yticks()
# plt.show()
#
# fig, (ax0, ax1) = plt.subplots(1, 2)
# Z = - MS.Smn_hat
# Z = np.flip(Z, axis=1)
# c = ax0.pcolor(Z, cmap='jet')
# c = ax1.pcolor(Z, edgecolors='k', linewidths=0.4)
# fig.tight_layout()
# plt.show()
#
# fig2,ax0 = plt.figure()
# plt.pcolor(Z.T, cmap='jet')
# plt.colorbar(shrink=.83)
# plt.xticks()
# plt.yticks()
# plt.show()

#
# while True:
#     try:
#         # sleep(0.5)
#         print("still recording")
#     except KeyboardInterrupt:
#         print("Ctrl+C pressed")
#         camera.stop_recording()
#         break

# from SerialPort import *
# com1 = 'COM3'
# com2 = 'COM6'
# UnitNum = 24
# Engine1 = Communication(com1, 115200, 0.5)
# Engine2 = Communication(com2, 115200, 0.5)
# Smn_hat_tempt = np.ones([UnitNum, UnitNum])
# Smn_hat_tempt1 = np.zeros([UnitNum, UnitNum])
# Pattern1 = Engine1.Image2hex(Smn_hat_tempt)
# Pattern2 = Engine1.Image2hex(Smn_hat_tempt1)
#
# Engine1.MetaDeploy(Pattern2)
# Engine2.MetaDeploy(Pattern2)
#
# for num in range(0,101,2):
#     print(num)
# from Seeker_SDK_Client import *
#
# # SetVerbosityLevel(4)
# # SetErrorMsgHandlerFunc(py_msg_func)
# print("Begin to init the SDK Client")
# ret = Initialize(b"10.1.1.198", b"10.1.1.198")
#
#
# # 获取天线位置
# def getATposi():
#     x_at = 0
#     y_at = 0
#     z_at = 0
#     b = 1
#
#     data = GetCurrentFrame()
#     frameData = data.contents
#     pBody = pointer(frameData.BodyData[0])
#
#     x_at = pBody.contents.Markers[0][0]
#     y_at = pBody.contents.Markers[0][1]
#     z_at = pBody.contents.Markers[0][2]
#
#     print('x', x_at, 'y', y_at, 'z', z_at)
#     return x_at, y_at, z_at
#
# def getSinglePoint():
#     data = GetCurrentFrame()
#     print("nUnidentifiedMarkers = %d" % data.contents.nUnidentifiedMarkers)
#     x = data.contents.UnidentifiedMarkers[0][0]
#     y = data.contents.UnidentifiedMarkers[0][1]
#     z = data.contents.UnidentifiedMarkers[0][2]
#
#     print('x', x, 'y', y, 'z', z)
#     return x, y, z
#
# # (x,y,z) = getSinglePoint()
# (x,y,z) = getATposi()

# 位置1 低
Location_Channel = np.array([1.3, 0.16, 2.237, -0.37, -0.08, 3.267]) #-1.4 X正向北 Y正向上
Location_Channel_up = np.array([0.07, 1.52, 1.476, 0.78, -0.44, 1.673])

fo = open("位置信息.csv", "wb")
print("文件名为: ", fo.name)
strr = "菜鸟教程"
fo.write(str(Location_Channel).encode("utf-8"))
fo.write(str(Location_Channel_up).encode("utf-8"))
np.savetxt(r"C:\Users\admin\Desktop\CCC_laptop\CCCans\new.csv", [Location_Channel, Location_Channel_up], delimiter = ',')
print([Location_Channel, Location_Channel_up])
# np.savetxt('new.csv', Location_Channel_up, delimiter = ',')

# import numpy
# my_matrix = numpy.loadtxt(open("c:\\1.csv","rb"),delimiter=",",skiprows=0)