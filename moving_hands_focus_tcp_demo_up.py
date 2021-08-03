# 此版本为天花板超材料版
from usrp_power_meter import *
import numpy as np
from SerialPort import *
from focus import *
import scipy.io as io
from matplotlib import pyplot as plt
import scipy.io as scio
import time
import matplotlib
import random
from Seeker_SDK_Client import *
from TCPmetasurface import *

UnitNum = 24
UnitNumY = 24
m_PRFdata = 10000

# 初始化各个模块-----------------------
# USRP
usrp, streamer, args, chan = SetUsrp()
# 超材料控制板（站立）
tcpHandle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpHandle.connect(("10.1.1.11", 7))
OnResetMod2(m_PRFdata, tcpHandle)
# 动捕系统初始化
print("Begin to init the SDK Client")
ret = Initialize(b"10.1.1.198", b"10.1.1.198")
# 动捕系统
(x_at, y_at, z_at) = getATposi()
Location_Channel_stand = np.array([1302.93, 1296.55-1146, -282.26+2500, -y_at, z_at -1146, x_at+2500]) / 1000  # -y_at,z_at -1146,x_at+2500  # -1.4 X正向北 Y正向上 # x_at, -y_at, 2654-z_at

MSstand = MetaSurface(Location_Channel_stand, UnitNum)
MSstand.GetMatePattern34()
Smn_hat_temp_stand = (MSstand.Smn_hat.copy() + 1) / 2  # 32*24 聚焦
Smn_hat_tempt_stand_all_off = np.ones([UnitNumY, UnitNum])

PowerMax_static = []
PowerPath_static = []

for num in range(1, 25):  # 测量全关状态下的信号值
    Pattern_hex = Image2hex33TCPMod2(Smn_hat_tempt_stand_all_off)
    OnPatternMod2onTime(Pattern_hex, tcpHandle)
    power = GetPower(streamer, args, chan)
    PowerMax_static = np.append(PowerMax_static, power)  # 编码变动前的功率值
    PowerPath_static = np.append(PowerPath_static, power)  # 全过程功率变动值
    time.sleep(0.03)
    recv_data = tcpHandle.recv(1024)
    print('receive on', recv_data)
for num in range(1, 25):  ##测量stand聚焦状态下的信号值
    # 优化编码
    (x_at, y_at, z_at) = getATposi()
    Location_Channel_up = np.array([4.37, -1742.16, 2654-1316.20, x_at, -y_at, 2654-z_at]) / 1000
    MSup = MetaSurface(Location_Channel_up, UnitNum)
    MSup.GetMatePattern()
    Smn_hat_temp_stand = (MSup.Smn_hat.copy() + 1) / 2  # 32*24 聚焦
    # 部署编码
    Pattern_hex = Image2hex33TCPMod2(Smn_hat_temp_stand)
    OnPatternMod2onTime(Pattern_hex, tcpHandle)
    # 测量功率
    power = GetPower(streamer, args, chan)
    PowerMax_static = np.append(PowerMax_static, power)
    PowerPath_static = np.append(PowerPath_static, power)

    recv_data = tcpHandle.recv(1024)
    print('receive on', recv_data)

while(1):
    (x_at, y_at, z_at) = getATposi()
    Location_Channel_up = np.array([4.37, -1742.16, 2654 - 1316.20, x_at, -y_at, 2654 - z_at]) / 1000
    MSup = MetaSurface(Location_Channel_up, UnitNum)
    MSup.GetMatePattern()
    Smn_hat_temp_stand = (MSup.Smn_hat.copy() + 1) / 2  # 32*24 聚焦
    # 部署编码
    Pattern_hex = Image2hex33TCPMod2(Smn_hat_temp_stand)
    OnPatternMod2onTime(Pattern_hex, tcpHandle)
    # 测量功率
    power = GetPower(streamer, args, chan)
    PowerMax_static = np.append(PowerMax_static, power)
    PowerPath_static = np.append(PowerPath_static, power)

    recv_data = tcpHandle.recv(1024)
    print('receive on', recv_data)
    time.sleep(0.02)

# fig, ax = plt.subplots(1, 2)
# c = ax[0].plot(PowerPath_static, '-r')
# ax[0].set_title("whole journey power")
# ax[1].pcolor(-MSstand.Smn_hat, cmap='jet', edgecolors='k', linewidths=0.4)
# plt.show()