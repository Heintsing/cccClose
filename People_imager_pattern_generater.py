from usrp_power_meter import *
import numpy as np
from SerialPort import *
from focus import *
import scipy.io as io
from matplotlib import pyplot as plt
import scipy.io as scio
import time
import random


com = 'COM5'
UnitNum = 24
UnitNumY = 32

# Location_Channel = np.array([0, 0, 2.654, 2.8, 0, 2.654])  #  -1.30, 0, 1.111
# Location_Channel = np.array([1.3, 0.16, 2.237, -0.00, 0.54, 2.449])  #  -1.30, 0, 1.111 位置1 X正向北 Y正向上
# Location_Channel = np.array([1.3, 0.16, 2.237, -0.70, 0.16, 3.090]) # 位置2
# Location_Channel = np.array([1.3, 0.16, 2.237, -0.00, 0.524, 2.230])  #  -1.30, 0, 1.111 位置1 X正向北 Y正向上 0630
Location_Channel = np.array([1.3, 0.16, 2.237, -0.8, 0.273, 3.070])  #  -1.30, 0, 1.111 位置1 X正向北 Y正向上 0630

Communication.Print_Used_Com()
Engine1 = Communication(com, 115200, 0.5)
Engine1.Print_Name()

row = 0
percent = 0
n = 0
MS = MetaSurface(Location_Channel, UnitNum)

Bit = []
for percent in range(0,97,50):#(0,97,4):
    Smn = np.ones([UnitNumY, UnitNum])  # 初始化为0
    # if n % 2 == 0:
    #     print(percent)
    #     num_percent = math.floor(percent / 100 * (UnitNumY) * (UnitNum))
    #     print(num_percent)
    #     # index = np.random.randint((UnitNumY) * (UnitNum), size=num_percent)
    #     index = random.sample(range(1, UnitNumY * UnitNum), num_percent)
    #     index = np.array(index)
    #     row = index // (UnitNum)
    #     column = index % (UnitNum)
    #     Smn[row.astype(int), column.astype(int)] = 0
    #     # print(Smn)
    #     # 串口控制
    #     Pattern = Engine1.Image2hex34(Smn)
    #     BitTemp = Engine1.MetaDeployMultiPattern(Pattern, n)
    #     Bit = np.append(Bit, BitTemp)
    # else:
    MS.GetMatePattern34Phase(np.floor(percent/100*2*np.pi))
    Smn = MS.Smn_hat
    # 串口控制
    Pattern = Engine1.Image2hex34((Smn+1)/2)
    BitTemp = Engine1.MetaDeployMultiPattern(Pattern, n)
    Bit = np.append(Bit, BitTemp)

    n = n+1

# fo = open("3224百分比递增0，4-100_间隔聚焦编码_位置一.txt", "wb")
fo = open("编码/3224间隔聚焦编码_位置二20210630.txt", "wb")
print ("文件名为: ", fo.name)
str = "菜鸟教程"
fo.write(Bit)

fig, (ax1) = plt.subplots(1, 1)
ax1.pcolor(MS.Smn_hat, cmap='jet', edgecolors='k', linewidths=0.4)
fig.tight_layout()
plt.show()