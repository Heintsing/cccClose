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
Resolution = 0.2  # 0.1m
VisionFiled = 1.4 # 1m的方形范围 %0.8
UnitNumY = 32
numGrid = int(VisionFiled / Resolution)
PowerMap = np.zeros([numGrid, numGrid])
Location_Channel = np.array([0.07, 1.527, 2.684-1.22, 2.8, 0, 2.654])  #  -1.30, 0, 1.111 X正向西 Y正向北 上北下南左西右东 1.482 2.47-1.1
Location_Channel_stand = np.array([1.3, 0.16, 2.237, -0.00, 0.54, 2.449]) #-1.4 X正向北 Y正向上

Communication.Print_Used_Com()
Engine1 = Communication(com, 115200, 0.5)
Engine1.Print_Name()

row = 0
column = 0
n=0
Bit = []
Smn = np.ones([UnitNumY, UnitNum])  # 初始化为0
for row in range(numGrid):
    for column in range(numGrid):
        if n % 2 == 0:
            # 优化波束指向
            Location_Channel = np.array(
                [Location_Channel[0], Location_Channel[1], Location_Channel[2], row * Resolution - VisionFiled / 2+2.8, column * Resolution - VisionFiled / 2,
                 2.665])  # 设定源的位置 0.9 X正向西 Y正向北 上北下南左西右东 1.482 2.47-1.1   -1.20 #2.474  2.683-0.95=1.733  2.68-1.582=1.098
            MS = MetaSurface(Location_Channel, UnitNum)
            # MS.GetMatePatternMIMO(0.1) #扩大聚焦点
            MS.GetMatePattern()
            # 串口控制
            Pattern = Engine1.Image2hex(MS.Smn_hat)
            BitTemp = Engine1.MetaDeployMultiPattern(Pattern,n)
            Bit = np.append(Bit, BitTemp)
        else:
            num_percent = math.floor(n*2 / 100 * (UnitNumY) * (UnitNum))
            print(num_percent)
            # index = np.random.randint((UnitNumY) * (UnitNum), size=num_percent)
            index = random.sample(range(1, UnitNumY * UnitNum), num_percent)
            index = np.array(index)
            row1 = index // (UnitNum)
            column1 = index % (UnitNum)
            Smn[row1.astype(int), column1.astype(int)] = 0
            # print(Smn)
            # 串口控制
            Pattern = Engine1.Image2hex34(Smn)
            BitTemp = Engine1.MetaDeployMultiPattern(Pattern, n)
            Bit = np.append(Bit, BitTemp)
        n = n + 1
print('sss')
row = 0
column = 0
n=0
Bit_stand = []
Smn = np.ones([UnitNumY, UnitNum])  # 初始化为0
for row in range(numGrid):
    for column in range(numGrid):
        if n % 2 == 0:
            print('n=',n)
            # 优化波束指向
            Location_Channel_stand = np.array(
                [Location_Channel_stand[0], Location_Channel_stand[1], Location_Channel_stand[2], row * Resolution - VisionFiled / 2, column * Resolution - VisionFiled / 2,
                 5.7])  # 设定源的位置 0.9 X正向西 Y正向北 上北下南左西右东 1.482 2.47-1.1   -1.20 #2.474  2.683-0.95=1.733  2.68-1.582=1.098
            MS34 = MetaSurface(Location_Channel_stand, UnitNum)
            # MS.GetMatePatternMIMO(0.1) #扩大聚焦点
            MS34.GetMatePattern34()
            # 串口控制
            Pattern = Engine1.Image2hex34((MS34.Smn_hat+1)/2)
            BitTemp = Engine1.MetaDeployMultiPattern(Pattern,n)
            Bit_stand = np.append(Bit_stand, BitTemp)
        else:
            num_percent = math.floor(n*2 / 100 * (UnitNumY) * (UnitNum))
            print('%====',num_percent)
            # index = np.random.randint((UnitNumY) * (UnitNum), size=num_percent)
            index = random.sample(range(1, UnitNumY * UnitNum), num_percent)
            index = np.array(index)
            row1 = index // (UnitNum)
            column1 = index % (UnitNum)
            Smn[row1.astype(int), column1.astype(int)] = 0
            # print(Smn)
            # 串口控制
            Pattern = Engine1.Image2hex34(Smn)
            BitTemp = Engine1.MetaDeployMultiPattern(Pattern, n)
            Bit_stand = np.append(Bit_stand, BitTemp)
        n = n+1

fo = open("Through_Wall_code_36_up_聚焦随机交织.txt", "wb")
print ("文件名为: ", fo.name)
str = "菜鸟教程"
fo.write(Bit)

fo = open("Through_Wall_code_36_stand_聚焦随机交织.txt", "wb")
print ("文件名为: ", fo.name)
str = "菜鸟教程"
fo.write(Bit_stand)