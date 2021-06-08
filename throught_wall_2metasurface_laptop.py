from usrp_power_meter import *
import numpy as np
from SerialPort import *
from focus import *
import scipy.io as io
from matplotlib import pyplot as plt
import scipy.io as scio
import time
import random

# Location_Channel = np.array([0, 0, 2.654, -2.8, 0, 2.654])  # 设定源的位置 0.9 X正向西 Y正向北 上北下南左西右东 1.482 2.47-1.1
Location_Channel = np.array([0, 0, 2.2, 0, -1.26, 0.95]) #-1.4 X正向北 Y正向上
Location_Channel_up = np.array([0, 0, 2.654, 1.4, 0, 2.654 - 1.3])
com1 = 'COM3'  # 竖着的
com2 = 'COM5'  # 天花板
UnitNum = 24
UnitNumY = 32

# 初始化各个模块-----------------------
usrp, streamer, args, chan = SetUsrp()

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
Smn_hat_record = np.zeros([1, UnitNumY, UnitNum])  # 初始化为0


MS = MetaSurface(Location_Channel, UnitNum)
MSup = MetaSurface(Location_Channel_up, UnitNum)
MS.GetMatePattern34()
MSup.GetMatePattern()
# Smn_hat_temp = np.ones([UnitNum, UnitNum]) #初始化为0
# Smn_hat = np.ones([UnitNum, UnitNum])
Smn_hat_temp = (MS.Smn_hat.copy() + 1) / 2      #32*24
Smn_hat_temp_up = (MSup.Smn_hat.copy() + 1) / 2 #24*24
# Smn_hat_temp1 = (MS.Smn_hat.copy() + 1) / 2
Smn_hat = (MS.Smn_hat.copy() + 1) / 2
Smn_hat_up = (MSup.Smn_hat.copy() + 1) / 2
Smn_hat_record = np.append(Smn_hat_record, [Smn_hat], axis=0)

powerTemp = GetPower(streamer, args, chan)
power_max = powerTemp.copy()
print(power_max, 'dbm')
fig, (ax0, ax1) = plt.subplots(1, 2)

for num in range(1, 25):
    Smn_hat_tempt = np.ones([UnitNumY, UnitNum])
    Pattern = Engine1.Image2hex34(Smn_hat_tempt)
    Engine1.MetaDeploy(Pattern)
    Engine2.MetaDeploy(Pattern)
    power = GetPower(streamer, args, chan)
    PowerMax_static = np.append(PowerMax_static, power)
    PowerPath_static = np.append(PowerPath_static, power)
    time.sleep(0.03)
for num in range(1, 25):
    Pattern = Engine1.Image2hex34(Smn_hat_temp)
    Pattern_up = Engine1.Image2hex(Smn_hat_temp_up)
    Engine1.MetaDeploy(Pattern)
    Engine2.MetaDeploy(Pattern_up)
    power = GetPower(streamer, args, chan)
    PowerMax_static = np.append(PowerMax_static, power)
    PowerPath_static = np.append(PowerPath_static, power)

# while 1:
# Smn_hat_temp = np.ones([UnitNumY, UnitNum]) #
for echo in range(1, 2):
    Smn_hat_temp = (MS.Smn_hat.copy() + 1) / 2
    # Smn_hat_temp = np.ones([UnitNumY, UnitNum]) #
    Smn_hat = (MS.Smn_hat.copy() + 1) / 2
    Smn_hat_record = np.zeros([1, UnitNumY, UnitNum])  # 初始化为0
    Smn_hat_record = np.append(Smn_hat_record, [Smn_hat], axis=0)
    PowerPath = []
    PowerMax = []
    Pattern = Engine1.Image2hex34(Smn_hat_temp)
    # Engine1.MetaDeploy(Pattern)
    # Engine2.MetaDeploy(Pattern)
    power_max = GetPower(streamer, args, chan)
    print('PowerMax', power_max)
    print('echo ', echo)


    start = time.time()
    power_last = GetPower(streamer, args, chan)
    for num in range(1, 500):
        if num != 1:
            index = np.random.randint((UnitNum-2) * (UnitNum-2))
            row = index // (UnitNum-2)+1
            column = index % (UnitNum-2)+1
            Smn_hat_temp_up[row-1:row+2, column-1:column+2] = (Smn_hat_temp_up[row-1:row+2, column-1:column+2] == False)
        Pattern_up = Engine2.Image2hex(Smn_hat_temp_up)
        Engine2.MetaDeploy(Pattern_up)
        # time.sleep(0.002)
        power = GetPower(streamer, args, chan)
        n = 1
        while not (np.abs(power_last-power) < 1.5):
            n = n + 1
            power = GetPower(streamer, args, chan)
            if n > 10:
                break
        if power > power_max:
            power_max = power.copy()
            Smn_hat = Smn_hat_temp_up.copy()
            Smn_hat_up = Smn_hat_temp_up.copy()
            print(power_max, 'dbm')
            Smn_hat = np.concatenate((np.ones([8, 24]), Smn_hat))
            Smn_hat_record = np.append(Smn_hat_record, [Smn_hat], axis=0)
            PowerMax = np.append(PowerMax, power_max)
        PowerPath = np.append(PowerPath, power)
        Smn_hat_temp_up = Smn_hat_up.copy()
        power_last = power.copy()
    print("top epoch took %.3f sec." % (time.time() - start))

    print('天花板')

    start = time.time()
    # Smn_hat_temp = np.ones([UnitNumY, UnitNum]) #
    power_last = GetPower(streamer, args, chan)
    for num in range(1, 500):
        # try:
        # 在原编码的基础上 随机改变10%的bit
        if num != 1:
            index = np.random.randint((UnitNumY-2) * (UnitNum-2))
            row = index // (UnitNumY-2)+1
            column = index % (UnitNum-2)+1
            Smn_hat_temp[row-1:row+2, column-1:column+2] = (Smn_hat_temp[row-1:row+2, column-1:column+2] == False)
        Pattern = Engine1.Image2hex34(Smn_hat_temp)
        Engine1.MetaDeploy(Pattern)
        time.sleep(0.02)
        power = GetPower(streamer, args, chan)
        n = 1
        while not (np.abs(power_last-power) < 1.5):
            n = n + 1
            power = GetPower(streamer, args, chan)
            if n > 10:
                break

        if (power > power_max) and (np.abs(power_last-power) < 2):
            power_max = power.copy()
            Smn_hat = Smn_hat_temp.copy()
            print(power_max, 'dbm')
            Smn_hat_record = np.append(Smn_hat_record, [Smn_hat], axis=0)
            PowerMax = np.append(PowerMax, power_max)
        PowerPath = np.append(PowerPath, power)
        Smn_hat_temp = Smn_hat.copy()
        power_last = power.copy()
    print("side epoch took %.3f sec." % (time.time() - start))


    PatternSavePath = r"C:\Users\admin\Desktop\CCC_laptop\CCCans\Smn_hat" + str(echo) + ".mat"
    scio.savemat(PatternSavePath, {'Smnhat': Smn_hat})
    PatternSavePath = r"C:\Users\admin\Desktop\CCC_laptop\CCCans\PowerPath" + str(echo) + ".mat"
    scio.savemat(PatternSavePath, {'Power': PowerPath})
    PatternSavePath = r"C:\Users\admin\Desktop\CCC_laptop\CCCans\Smn_hat_record" + str(echo) + ".mat"
    scio.savemat(PatternSavePath, {'Smn_hat_record': Smn_hat_record})
    PatternSavePath = r"C:\Users\admin\Desktop\CCC_laptop\CCCans\PowerMax" + str(echo) + ".mat"
    scio.savemat(PatternSavePath, {'PowerMax': PowerMax})

PatternSavePath = r"C:\Users\admin\Desktop\CCC_laptop\CCCans\PowerMax_static.mat"
scio.savemat(PatternSavePath, {'PowerMax_static': PowerMax_static})
PatternSavePath = r"C:\Users\admin\Desktop\CCC_laptop\CCCans\PowerPath_static.mat"
scio.savemat(PatternSavePath, {'PowerPath_static': PowerPath_static})

fig, (ax0, ax1, ax2) = plt.subplots(1, 3)
c = ax0.plot(PowerPath, '-r')
ax1.pcolor(MS.Smn_hat, cmap='jet', edgecolors='k', linewidths=0.4)
ax2.pcolor(MSup.Smn_hat, cmap='jet', edgecolors='k', linewidths=0.4)
fig.tight_layout()
plt.show()
# break
# 3007278564

