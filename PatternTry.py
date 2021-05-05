from usrp_power_meter import *
import numpy as np
from SerialPort import *
from focus import *
import scipy.io as io
from matplotlib import pyplot as plt
import scipy.io as scio
import time

Location_Channel = np.array([-1.20, 0, 1.37, 0.0, 0.0, 2.474])  # 设定源的位置 0.9 X正向西 Y正向北 上北下南左西右东 1.482 2.47-1.1
com = 'COM6'
UnitNum = 24

# 初始化各个模块-----------------------
usrp, streamer, args, chan = SetUsrp()

Communication.Print_Used_Com()
Engine1 = Communication(com, 115200, 0.5)
Engine1.Print_Name()

Smn_hat = np.ones([24,24])
powerTemp = GetPower(streamer, args, chan)
for row in range(UnitNum):
    for column in range(UnitNum):
        Smn_hat[row, column] = 1
        power = GetPower(streamer, args, chan)
        print(power, 'dbm')
        if power<powerTemp:
            Smn_hat[row, column] = 0
        Pattern = Engine1.Image2hex(Smn_hat)
        Engine1.MetaDeploy(Pattern)

PatternSavePath = r"F:\zht\CCC\CCCcloseData\analys\Smn_hat.mat"
scio.savemat(PatternSavePath, {'Smnhat': Smn_hat})



