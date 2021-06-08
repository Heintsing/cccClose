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
Resolution = 0.1  # 0.1m
VisionFiled = 0.8 # 1m的方形范围
numGrid = int(VisionFiled / Resolution)
PowerMap = np.zeros([numGrid, numGrid])
Location_Channel = np.array([0, 0, 2.654, 2.8, 0, 2.654])  #  -1.30, 0, 1.111

Communication.Print_Used_Com()
Engine1 = Communication(com, 115200, 0.5)
Engine1.Print_Name()

row = 0
column = 0
n=0
Bit = []
for row in range(numGrid):
    for column in range(numGrid):
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
        n = n+1

fo = open("Through_Wall_code_64.txt", "wb")
print ("文件名为: ", fo.name)
str = "菜鸟教程"
fo.write(Bit)