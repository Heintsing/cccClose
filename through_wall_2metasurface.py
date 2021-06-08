from usrp_power_meter import *
import numpy as np
from SerialPort import *
from focus import *
import scipy.io as io
from matplotlib import pyplot as plt
import scipy.io as scio
import time
import random
# from depth_sensing import *
# from FLANN2 import *

Location_Channel = np.array([0, 0, 2.654, -2.8, 0, 2.654])  # 设定源的位置 0.9 X正向西 Y正向北 上北下南左西右东 1.482 2.47-1.1
com1 = 'COM3'
com2 = 'COM5'
UnitNum = 24

# 初始化各个模块-----------------------
usrp, streamer, args, chan = SetUsrp()
point_cloud, zed, res = OpenCamera()

# Communication.Print_Used_Com()
Engine1 = Communication(com1, 115200, 0.5)
Engine1.Print_Name()
Engine2 = Communication(com2, 115200, 0.5)
Engine2.Print_Name()
t = []
m = []
PowerPath = []
PowerMax = []
PowerMax_static = []
PowerPath_static = []
num = 0
# template = cv2.imread('PKU.png', 0)
# Posipre = [[1104, 621]]
Smn_hat_record = np.zeros([1, UnitNum, UnitNum])  # 初始化为0

# 初始化Pattern 使用解析聚焦算法
# trans, Posipre = FLANN(zed, template, Posipre)  # 3.快速临近点匹配
# Location_Channel[3] = trans[0] - 0.7  # 0.862
# Location_Channel[4] = trans[1]
# Location_Channel[5] = -trans[2]
MS = MetaSurface(Location_Channel, UnitNum)
MS.GetMatePattern()
# Smn_hat_temp = np.ones([UnitNum, UnitNum]) #初始化为0
# Smn_hat = np.ones([UnitNum, UnitNum])
Smn_hat_temp = (MS.Smn_hat.copy() + 1) / 2
Smn_hat_temp1 = (MS.Smn_hat.copy() + 1) / 2
Smn_hat = (MS.Smn_hat.copy() + 1) / 2
Smn_hat_record = np.append(Smn_hat_record, [Smn_hat], axis=0)

powerTemp = GetPower(streamer, args, chan)
power_max = powerTemp.copy()
print(power_max, 'dbm')
fig, (ax0, ax1) = plt.subplots(1, 2)

for num in range(1, 25):
    Smn_hat_tempt = np.ones([UnitNum, UnitNum])
    Pattern = Engine1.Image2hex(Smn_hat_tempt)
    Engine1.MetaDeploy(Pattern)
    Engine2.MetaDeploy(Pattern)
    power = GetPower(streamer, args, chan)
    PowerMax_static = np.append(PowerMax_static, power)
    PowerPath_static = np.append(PowerPath_static, power)
    time.sleep(0.03)
for num in range(1, 25):
    Pattern = Engine1.Image2hex(Smn_hat_temp)
    Engine1.MetaDeploy(Pattern)
    Engine2.MetaDeploy(Pattern)
    power = GetPower(streamer, args, chan)
    PowerMax_static = np.append(PowerMax_static, power)
    PowerPath_static = np.append(PowerPath_static, power)

# while 1:
for echo in range(1, 4):
    Smn_hat_temp = (MS.Smn_hat.copy() + 1) / 2
    Smn_hat = (MS.Smn_hat.copy() + 1) / 2
    Smn_hat_record = np.zeros([1, UnitNum, UnitNum])  # 初始化为0
    Smn_hat_record = np.append(Smn_hat_record, [Smn_hat], axis=0)
    PowerPath = []
    PowerMax = []
    Pattern = Engine1.Image2hex(Smn_hat_temp)
    Engine1.MetaDeploy(Pattern)
    Engine2.MetaDeploy(Pattern)
    power_max = GetPower(streamer, args, chan)
    print('PowerMax', power_max)
    print('echo ', echo)
    for num in range(1, 1500):
        # try:
        # start = time.time()
        # 在原编码的基础上 随机改变10%的bit
        if num != 1:
            index = np.random.randint((UnitNum-2) * (UnitNum-2))
            row = index // (UnitNum-2)+1
            column = index % (UnitNum-2)+1
            Smn_hat_temp[row-1:row+2, column-1:column+2] = (Smn_hat_temp[row-1:row+2, column-1:column+2] == False)
            index = np.random.randint((UnitNum-2) * (UnitNum-2))
            row = index // (UnitNum-2)+1
            column = index % (UnitNum-2)+1
            Smn_hat_temp1[row-1:row+2, column-1:column+2] = (Smn_hat_temp1[row-1:row+2, column-1:column+2] == False)
        # Smn_hat_temp[index // UnitNum, index % UnitNum] = ~Smn_hat_temp[index // UnitNum, index % UnitNum]
        Pattern = Engine1.Image2hex(Smn_hat_temp)
        Engine1.MetaDeploy(Pattern)
        Pattern1 = Engine2.Image2hex(Smn_hat_temp1)
        Engine2.MetaDeploy(Pattern1)
        # print("串口控制 took %.3f sec." % (time.time() - start))
        # 测试功率是否变大
        power = GetPower(streamer, args, chan)
        if power > power_max:
            power_max = power.copy()
            Smn_hat = Smn_hat_temp.copy()
            print(power_max, 'dbm')
            Smn_hat_record = np.append(Smn_hat_record, [Smn_hat], axis=0)
            PowerMax = np.append(PowerMax, power_max)
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

    PatternSavePath = r"F:\zht\CCC\CCCcloseData\analys\TryPattern\Smn_hat" + str(echo) + ".mat"
    scio.savemat(PatternSavePath, {'Smnhat': Smn_hat})
    PatternSavePath = r"F:\zht\CCC\CCCcloseData\analys\TryPattern\PowerPath" + str(echo) + ".mat"
    scio.savemat(PatternSavePath, {'Power': PowerPath})
    PatternSavePath = r"F:\zht\CCC\CCCcloseData\analys\TryPattern\Smn_hat_record" + str(echo) + ".mat"
    scio.savemat(PatternSavePath, {'Smn_hat_record': Smn_hat_record})
    PatternSavePath = r"F:\zht\CCC\CCCcloseData\analys\TryPattern\PowerMax" + str(echo) + ".mat"
    scio.savemat(PatternSavePath, {'PowerMax': PowerMax})

PatternSavePath = r"F:\zht\CCC\CCCcloseData\analys\TryPattern\PowerMax_static.mat"
scio.savemat(PatternSavePath, {'PowerMax_static': PowerMax_static})
PatternSavePath = r"F:\zht\CCC\CCCcloseData\analys\TryPattern\PowerPath_static.mat"
scio.savemat(PatternSavePath, {'PowerPath_static': PowerPath_static})

fig, (ax0, ax1) = plt.subplots(1, 2)
c = ax0.plot(PowerPath, '-r')
c = ax1.pcolor(Smn_hat, cmap='jet', edgecolors='k', linewidths=0.4)
fig.tight_layout()
plt.show()
# break
# 3007278564

