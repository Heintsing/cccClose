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
PowerPath = []
num = 0

Smn_hat_temp = np.ones([UnitNum,UnitNum])
Smn_hat = np.ones([UnitNum,UnitNum])
powerTemp = GetPower(streamer, args, chan)
power_max = powerTemp.copy()
print(power_max, 'dbm')
fig, (ax0, ax1) = plt.subplots(1, 2)


# while 1:
for num in range(1, 1000):
    # try:
    start = time.time()
    index = np.random.randint(UnitNum * UnitNum, size=80)
    # 在原编码的基础上 随机改变10%的bit
    Smn_hat_temp[index // UnitNum, index % UnitNum] = (Smn_hat_temp[index // UnitNum, index % UnitNum] == False)
    # Smn_hat_temp[index // UnitNum, index % UnitNum] = ~Smn_hat_temp[index // UnitNum, index % UnitNum]
    Pattern = Engine1.Image2hex(Smn_hat_temp)
    Engine1.MetaDeploy(Pattern)
    # 测试功率是否变大
    power = GetPower(streamer, args, chan)
    if power > power_max:
        power_max = power.copy()
        Smn_hat = Smn_hat_temp.copy()
        print(power_max, 'dbm')
        # c = ax1.pcolor(Smn_hat, cmap='jet', edgecolors='k', linewidths=0.4)
    # print(power, 'dbm')
    # if power > powerTemp:
    #     Smn_hat = Smn_hat_temp.copy()

    powerTemp = power
    PowerPath = np.append(PowerPath, power)
    Smn_hat_temp = Smn_hat.copy()

    # start = time.time()
    # t_now = num
    # t.append(t_now)  # 模拟数据增量流入，保存历史数据
    # m.append(power)
    #
    # ax0.plot(t, m, '-r')
    # plt.draw()  # 注意此函数需要调用
    #
    # plt.pause(0.001)
    #     # plt.clf()  # 清空画布上的所有内容
    #     # num += 1
    # # except KeyboardInterrupt:
    # print("串口控制 took %.3f sec." % (time.time() - start))
    # 实时绘图因为后面数据量比较大，绘图会越来越慢


PatternSavePath = r"F:\zht\CCC\CCCcloseData\analys\TryPattern\Smn_hat.mat"
scio.savemat(PatternSavePath, {'Smnhat': Smn_hat})
PatternSavePath = r"F:\zht\CCC\CCCcloseData\analys\TryPattern\Power.mat"
scio.savemat(PatternSavePath, {'Power': PowerPath})

fig, (ax0, ax1) = plt.subplots(1, 2)
c = ax0.plot(PowerPath, '-r')
c = ax1.pcolor(Smn_hat, cmap='jet', edgecolors='k', linewidths=0.4)
fig.tight_layout()
plt.show()


print('aaa')
# break



