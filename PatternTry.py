from usrp_power_meter import *
import numpy as np
from SerialPort import *
from focus import *
import scipy.io as io
from matplotlib import pyplot as plt
import scipy.io as scio
import time
import random

Location_Channel = np.array([-1.20, 0, 1.37, 0.0, 0.0, 2.474])  # 设定源的位置 0.9 X正向西 Y正向北 上北下南左西右东 1.482 2.47-1.1
com = 'COM6'
UnitNum = 24

# 初始化各个模块-----------------------
usrp, streamer, args, chan = SetUsrp()

Communication.Print_Used_Com()
Engine1 = Communication(com, 115200, 0.5)
Engine1.Print_Name()
t = []
m = []


Smn_hat_temp = np.ones([UnitNum,UnitNum])
Smn_hat = np.ones([UnitNum,UnitNum])
powerTemp = GetPower(streamer, args, chan)
# for row in range(UnitNum):
#     for column in range(UnitNum):
#         Smn_hat[row, column] = 1
#         power = GetPower(streamer, args, chan)
#         print(power, 'dbm')
#         if power<powerTemp:
#             Smn_hat[row, column] = 0
#         Pattern = Engine1.Image2hex(Smn_hat)
#         Engine1.MetaDeploy(Pattern)
try:
    while 1:
        index = np.random.randint(UnitNum * UnitNum, size=80)
        # 在原编码的基础上 随机改变10%的bit
        Smn_hat_temp[index // UnitNum, index % UnitNum] = 1
        Pattern = Engine1.Image2hex(Smn_hat_temp)
        Engine1.MetaDeploy(Pattern)
        # 测试功率是否变大
        power = GetPower(streamer, args, chan)
        print(power, 'dbm')
        if power > powerTemp:
            Smn_hat = Smn_hat_temp

        powerTemp = power
        Smn_hat_temp = Smn_hat

        plt.clf()  # 清空画布上的所有内容
        t_now = num
        t.append(t_now)  # 模拟数据增量流入，保存历史数据
        m.append(power)
        plt.plot(t, m, '-r')
        plt.draw()  # 注意此函数需要调用

        plt.pause(0.001)
except:
    PatternSavePath = r"F:\zht\CCC\CCCcloseData\analys\Smn_hat.mat"
    scio.savemat(PatternSavePath, {'Smnhat': Smn_hat})

    fig = plt.figure()
    plt.pcolor(Smn_hat, cmap='jet', edgecolors='k', linewidths=0.4)
    plt.colorbar(shrink=.83)
    plt.xticks()
    plt.yticks()
    plt.show()



