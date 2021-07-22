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

# Location_Channel = np.array([0, 0, 2.654, -2.8, 0, 2.654])  # 设定源的位置 0.9 X正向西 Y正向北 上北下南左西右东 1.482 2.47-1.1
# Location_Channel = np.array([0, 0, 2.2, 0, -1.26, 0.95]) #-1.4 X正向北 Y正向上
# Location_Channel_up = np.array([0, 0, 2.654, 1.4, 0, 2.654 - 1.3])
# 20210701
# # 位置1 低
# Location_Channel = np.array([1.3, 0.16, 2.237, -0.37, -0.08, 3.267]) #-1.4 X正向北 Y正向上
# Location_Channel_up = np.array([0.07, 1.52, 1.476, 0.78, -0.44, 1.673])
# # 位置2 高
# # Location_Channel = np.array([1.3, 0.16, 2.237, 0.0, 0.2, 2.464]) #-1.4 X正向北 Y正向上
# # Location_Channel_up = np.array([0.07, 1.52, 1.476, -0.00, -0.0, 1.4383])

com1 = 'COM10'  # 天花板
com2 = 'COM7'  # 竖着的
UnitNum = 24
UnitNumY = 32
n_switch = 1000

# 初始化各个模块-----------------------
usrp, streamer, args, chan = SetUsrp()
# Communication.Print_Used_Com()
Engine1 = Communication(com1, 115200, 0.5)
Engine1.Print_Name()
Engine2 = Communication(com2, 115200, 0.5)
Engine2.Print_Name()
# 动捕系统初始化
print("Begin to init the SDK Client")
ret = Initialize(b"10.1.1.198", b"10.1.1.198")
# 变量初始化
t = []
m = []
PowerPath = []
PowerMax = []
PowerMax_static = []
PowerPath_static = []
num = 0
Smn_hat_record = np.zeros([1, UnitNumY, UnitNum])  # 初始化为0

# 获取天线位置
# 动捕系统版本
(x_at, y_at, z_at) = getATposi()
Location_Channel = np.array([1302.93, 1296.55-1146, -282.26+2500, -y_at, z_at -1146, x_at+2500]) / 1000  # -y_at,z_at -1146,x_at+2500  # -1.4 X正向北 Y正向上 # x_at, -y_at, 2654-z_at
Location_Channel_up = np.array([4.37, -1742.16, 2654-1316.20, x_at, -y_at, 2654-z_at]) / 1000

print('Location_Channel',Location_Channel)
print('Location_Channel_up',Location_Channel_up)

MS = MetaSurface(Location_Channel, UnitNum)
MSup = MetaSurface(Location_Channel_up, UnitNum)
MS.GetMatePattern34()
MSup.GetMatePattern()
# 优化得到常用编码
Smn_hat_temp_stand = (MS.Smn_hat.copy() + 1) / 2  # 32*24 聚焦
Smn_hat_temp_up = (MSup.Smn_hat.copy() + 1) / 2  # 24*24
Smn_hat_tempt_up_all_off = np.ones([UnitNum, UnitNum])
Smn_hat_tempt_stand_all_off = np.ones([UnitNumY, UnitNum])

Smn_hat = (MS.Smn_hat.copy() + 1) / 2
Smn_hat_stand = (MS.Smn_hat.copy() + 1) / 2
Smn_hat_up = (MSup.Smn_hat.copy() + 1) / 2
Smn_hat_record = np.append(Smn_hat_record, [Smn_hat], axis=0)  # 优化pattern真值记录

powerTemp = GetPower(streamer, args, chan)
power_max = powerTemp.copy()
print(power_max, 'dbm')

for num in range(1, 25):  # 测量全关状态下的信号值
    Pattern_up = Engine1.Image2hex(Smn_hat_tempt_up_all_off)
    Pattern_stand = Engine1.Image2hex34(Smn_hat_tempt_stand_all_off)
    Engine1.MetaDeploy(Pattern_up)
    Engine2.MetaDeploy(Pattern_stand)
    power = GetPower(streamer, args, chan)
    PowerMax_static = np.append(PowerMax_static, power)  # 编码变动前的功率值
    PowerPath_static = np.append(PowerPath_static, power)  # 全过程功率变动值
    time.sleep(0.03)
for num in range(1, 25):  ##测量stand聚焦状态下的信号值
    Pattern_stand = Engine1.Image2hex34(Smn_hat_temp_stand)
    Pattern_up = Engine1.Image2hex(Smn_hat_tempt_up_all_off)
    Engine1.MetaDeploy(Pattern_up)
    Engine2.MetaDeploy(Pattern_stand)
    power = GetPower(streamer, args, chan)
    PowerMax_static = np.append(PowerMax_static, power)
    PowerPath_static = np.append(PowerPath_static, power)
for num in range(1, 25):  ##测量up聚焦状态下的信号值
    Pattern_stand = Engine1.Image2hex34(Smn_hat_tempt_stand_all_off)
    Pattern_up = Engine1.Image2hex(Smn_hat_temp_up)
    Engine1.MetaDeploy(Pattern_up)
    Engine2.MetaDeploy(Pattern_stand)
    power = GetPower(streamer, args, chan)
    PowerMax_static = np.append(PowerMax_static, power)
    PowerPath_static = np.append(PowerPath_static, power)
for num in range(1, 25):  ##测量双超材料同时聚焦状态下的信号值
    Pattern_stand = Engine1.Image2hex34(Smn_hat_temp_stand)
    Pattern_up = Engine1.Image2hex(Smn_hat_temp_up)
    Engine1.MetaDeploy(Pattern_up)
    Engine2.MetaDeploy(Pattern_stand)
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
    # 不使用双聚焦，吊顶超材料仅用作后续优化 需要调整两个地方
    Pattern_stand = Engine2.Image2hex34(Smn_hat_temp_stand)
    Pattern_up = Engine1.Image2hex(Smn_hat_temp_up)  # mark1
    Engine1.MetaDeploy(Pattern_up)
    Engine2.MetaDeploy(Pattern_stand)
    power_max = GetPower(streamer, args, chan)
    print('PowerMax', power_max)
    print('echo ', echo)

    start = time.time()
    power_last = GetPower(streamer, args, chan)
    n_stand_pattern_true = 0  # 优化成功的次数
    for num in range(1, n_switch):
        if num != 1:  # 随机翻转状态
            index = np.random.randint((UnitNumY - 2) * (UnitNum - 2))
            row = index // (UnitNumY - 2) + 1
            column = index % (UnitNum - 2) + 1
            Smn_hat_temp_stand[row - 1:row + 2, column - 1:column + 2] = (Smn_hat_temp_stand[row - 1:row + 2, column - 1:column + 2] == False)
        # 部署超材料编码
        Pattern_stand = Engine2.Image2hex34(Smn_hat_temp_stand)
        Engine2.MetaDeploy(Pattern_stand)
        # time.sleep(0.002)
        power = GetPower(streamer, args, chan)
        n = 1
        # 滤除特大干扰
        while not (np.abs(power_last - power) < 1.5):
            n = n + 1
            power = GetPower(streamer, args, chan)
            if n > 10:
                break
        if power > power_max:
            power_max = power.copy()
            Smn_hat = Smn_hat_temp_stand.copy()  # 用于修正3*3 与3*4pattern的差距，保证可以放在一个数组里
            Smn_hat_stand = Smn_hat_temp_stand.copy()
            print(power_max, 'dbm')
            Smn_hat_record = np.append(Smn_hat_record, [Smn_hat], axis=0)  # 记录优化过程编码变化
            PowerMax = np.append(PowerMax, power_max)
            n_stand_pattern_true = n_stand_pattern_true + 1
        PowerPath = np.append(PowerPath, power)
        Smn_hat_temp_stand = Smn_hat.copy()
        power_last = power.copy()
    print("top epoch took %.3f sec." % (time.time() - start))
    print("number of true stand metasurface pattern", n_stand_pattern_true)

    print('天花板,start!')
    start = time.time()
    # Smn_hat_temp = np.ones([UnitNumY, UnitNum]) #

    # Smn_hat_temp_up = Smn_hat_tempt_up_all_off.copy()
    # Smn_hat_up = Smn_hat_temp_up.copy() # 迭代需要，否则会报错和设为初始值   # mark2
    power_last = GetPower(streamer, args, chan)
    n_up_pattern_true = 0
    for num in range(1, n_switch):
        if num != 1:
            index = np.random.randint((UnitNum - 2) * (UnitNum - 2))
            row = index // (UnitNum - 2) + 1
            column = index % (UnitNum - 2) + 1
            Smn_hat_temp_up[row - 1:row + 2, column - 1:column + 2] = (Smn_hat_temp_up[row - 1:row + 2, column - 1:column + 2] == False)
        Pattern_up = Engine1.Image2hex(Smn_hat_temp_up)
        Engine1.MetaDeploy(Pattern_up)
        # time.sleep(0.02)
        power = GetPower(streamer, args, chan)
        n = 1
        while not (np.abs(power_last - power) < 1.5):
            n = n + 1
            power = GetPower(streamer, args, chan)
            if n > 20:
                break
        if power > power_max:
            power_max = power.copy()
            Smn_hat = Smn_hat_temp_up.copy()
            Smn_hat_up = Smn_hat_temp_up.copy()
            print(power_max, 'dbm')
            Smn_hat = np.concatenate((np.ones([8, 24]), Smn_hat))
            Smn_hat_record = np.append(Smn_hat_record, [Smn_hat], axis=0)
            PowerMax = np.append(PowerMax, power_max)
            n_up_pattern_true = n_up_pattern_true + 1
        PowerPath = np.append(PowerPath, power)
        Smn_hat_temp_up = Smn_hat_up.copy()  # 在真值基础上进一步优化
        power_last = power.copy()
    print("stand epoch took %.3f sec." % (time.time() - start))
    print("number of true stand metasurface pattern", n_up_pattern_true)

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

Pattern_up = Engine1.Image2hex(Smn_hat_up)
Pattern_stand = Engine2.Image2hex34(Smn_hat_stand)
Bit_up = Engine1.MetaDeployMultiPattern(Pattern_up, 0)
Bit_stand = Engine1.MetaDeployMultiPattern(Pattern_stand, 0)
fo = open("2424联合在线优化编码_位置高20210707.txt", "wb")
print("文件名为: ", fo.name)
str = "菜鸟教程"
fo.write(Bit_up)
fo = open("3224联合在线优化编码_位置高20210707.txt", "wb")
print("文件名为: ", fo.name)
str = "菜鸟教程"
fo.write(Bit_stand)

fig, ax = plt.subplots(2, 3)
# 设置字体为楷体
# matplotlib.rcParams['font.sans-serif'] = ['SimHei']
# matplotlib.rcParams['figure.autolayout'] = True
fig.suptitle('metasurface pattern optimize')
c = ax[0, 0].plot(PowerPath, '-r')
ax[0, 0].set_title("whole journey power")
ax[0, 1].pcolor(-MS.Smn_hat, cmap='jet', edgecolors='k', linewidths=0.4)
ax[0, 2].pcolor(-MSup.Smn_hat.T, cmap='jet', edgecolors='k', linewidths=0.4)
PowerPath = np.append(PowerMax_static, PowerMax)
ax[1, 0].plot(PowerPath, '-r')
ax[1, 0].set_title("meaningful power record")
ax[1, 1].pcolor(-Smn_hat_stand, cmap='jet', edgecolors='k', linewidths=0.4)  # Smn_hat_temp_stand
ax[1, 2].pcolor(-Smn_hat_up.T, cmap='jet', edgecolors='k', linewidths=0.4)  # Smn_hat_temp_up
# fig.tight_layout()
plt.savefig('超材料在线编码优化.png')
plt.show()

# break
# 3007278564
