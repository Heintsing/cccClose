#!/usr/bin/python
# -*- coding: UTF-8 -*-

from SerialPort import *
from focus import *
from depth_sensing import *
from usrp_power_meter import *
from ObjectDetect import *
from FLANN2 import *
import numpy as np
from matplotlib import pyplot as plt
from TCPsend import *
import scipy.io as scio


# 1.设置串口
# 2.设置USRP IP
# 3.设置超表面单元数目和工作频段
# 4.准确设置发射机或接收机坐标
# 5.设置光学定位匹配模板
# 6.在笔记本上运行运动控制程序
# 7.小车开启roscore
# 8.小车放至起始位置
# 9.打开矢网和超材料电源
# 10.设置采样点数
# 11.设置数据保存路径


def plotPosi(Posi):
    plt.plot(Posi[:, 0:2])
    plt.show()


# pyserial pyopengl
# Location_Channel = np.array([0.07, -1.79, 1.184, 0.5, 0.2, 1.7])  # 设定源的位置 0.9 X正向西 Y正向北 上北下南左西右东
Location_Channel = np.array([-1.20, 0, 1.37, 0.0, 0.0, 2.474])  # 设定源的位置 0.9 X正向西 Y正向北 上北下南左西右东 1.482 2.47-1.1
com = 'COM6'
UnitNum = 24

# 初始化各个模块
point_cloud, zed, res = OpenCamera()
usrp, streamer, args, chan = SetUsrp()
template = cv2.imread('PKU.png', 0)
tcp_socket = TcpConnect()

Communication.Print_Used_Com()
Engine1 = Communication(com, 115200, 0.5)
Engine1.Print_Name()
t = []
m = []
PowerPath = []
Posipre = [[1104, 621]]
Posi = np.zeros([1, 3])

plt.ion()  # 开启interactive mode 成功的关键函数
plt.figure(1)
for num in range(1, 40):
    TcpsSend(tcp_socket)  # 控制小车运动 #小车指令未执行完会被刷新
    time.sleep(2)

    Forstart = time.time()
    # 定位------------
    start = time.time()
    # GrabPointCloud(point_cloud, zed, res)  # 光学定位
    # trans = GetTrans(point_cloud)  # 1.点云ICP配准法
    # point_cloud_np = point_cloud.get_data()  # 2.位置平均法
    # trans = cutZed(point_cloud_np)

    trans, Posipre = FLANN(zed, template, Posipre)  # 3.快速临近点匹配
    a = np.copy(trans).reshape(-1, 3)
    Posi = np.append(Posi, a, axis=0)
    Location_Channel[3] = trans[0] - 0.7  # 0.862
    Location_Channel[4] = trans[1]
    Location_Channel[5] = -trans[2]
    print("光学定位 took %.3f sec." % (time.time() - start))
    # 聚焦------------
    start = time.time()
    MS = MetaSurface(Location_Channel, UnitNum)
    MS.GetMatePattern()
    print("编码优化 took %.3f sec." % (time.time() - start))

    # MS.Smn_hat
    # print(MS.Smn_hat)
    # MS.Smn_hat = np.zeros([24,24])

    # 串口控制---------
    start = time.time()
    Pattern = Engine1.Image2hex(MS.Smn_hat)
    # Pattern = Engine1.Image2hex(-np.ones([24,24]))
    # a = -np.ones([24,24])
    # c=np.concatenate((-np.ones([12,24]), np.ones([12,24])),axis=0)
    # Pattern = Engine1.Image2hex(c)
    Engine1.MetaDeploy(Pattern)
    print("串口控制 took %.3f sec." % (time.time() - start))
    # 测量功率----------
    for i in range(1, 11):
        start = time.time()
        power = GetPower(streamer, args, chan)
        # print("acquire signal Power took %.3f sec." % (time.time() - start))
        print("功率测量 took %.3f sec." % (time.time() - start))
        # PowerPath[num] = power  # 模拟数据增量流入，保存历史数据
        PowerPath = np.append(PowerPath, power)

    # MS.Smn_hat = np.zeros([24, 24])
    Location_Channel = np.array([-1.20, 0, 1.37, 2.0, -2.0, 2.474])
    MS = MetaSurface(Location_Channel, UnitNum)
    MS.GetMatePattern()
    Pattern = Engine1.Image2hex(MS.Smn_hat)
    Engine1.MetaDeploy(Pattern)

    for i in range(1, 11):
        start = time.time()
        power = GetPower(streamer, args, chan)
        # print("acquire signal Power took %.3f sec." % (time.time() - start))
        print("功率测量 took %.3f sec." % (time.time() - start))
        # PowerPath[num] = power  # 模拟数据增量流入，保存历史数据
        PowerPath = np.append(PowerPath, power)


    start = time.time()
    plt.clf()  # 清空画布上的所有内容
    t_now = num
    t.append(t_now)  # 模拟数据增量流入，保存历史数据
    m.append(power)
    plt.plot(t, m, '-r')
    plt.draw()  # 注意此函数需要调用

    plt.pause(0.001)

    # TcpsReceive(tcp_socket)  # 确认小车完成一次运动
    # print("draw figure took %.3f sec." % (time.time() - start))
    print("更新曲线 took %.3f sec." % (time.time() - start))
    print("闭环时间 took %.3f sec.\n" % (time.time() - Forstart))
    # time.sleep(3)

# np.save(r"F:\zht\CCC\cccClose\m.mat", m)
dataCarPosi = r"F:\zht\CCC\cccClose\draw\TraceON&OFF.mat"
dataPower = r"F:\zht\CCC\cccClose\draw\PowerON&OFF.mat"
scio.savemat(dataCarPosi, {'PosiONOFF': Posi})
scio.savemat(dataPower, {'PowerONOFF': PowerPath})
# time.sleep(10)
plotPosi(Posi)
# 预留显示时间
time.sleep(5)
# 绘制超材料编码
filename = r"C:\Users\admin\PycharmProjects\temp\figure"

fig, (ax0, ax1) = plt.subplots(1, 2)
Z = - MS.Smn_hat
Z = np.flip(Z, axis=1)
c = ax0.pcolor(Z, cmap='jet')
ax0.set_title('default: no edges')
c = ax1.pcolor(Z, edgecolors='k', linewidths=0.4)
ax1.set_title('thick edges')
fig.tight_layout()
plt.show()

fig2 = plt.figure()
plt.pcolor(Z.T, cmap='jet')
plt.colorbar(shrink=.83)
plt.xticks()
plt.yticks()
plt.show()

# 绘制聚焦平面

# 关闭各个模块
CloseZed(zed)
# TcpClose(tcp_socket)
