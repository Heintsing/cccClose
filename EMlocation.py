from usrp_power_meter import *
import numpy as np
from SerialPort import *
from focus import *
from matplotlib import pyplot as plt
import scipy.io as io
import time

com = 'COM5'
UnitNum = 24
Resolution = 0.05  # 0.1m
VisionFiled = 4 # 1m的方形范围
numGrid = int(VisionFiled / Resolution)
PowerMap = np.zeros([numGrid, numGrid])
Location_Channel = np.array([0, 0, 2.654, -2.8, 0, 2.654])  #  -1.30, 0, 1.111

usrp, streamer, args, chan = SetUsrp()
Communication.Print_Used_Com()
Engine1 = Communication(com, 115200, 0.5)
Engine1.Print_Name()
start = time.time()

row = 0
column = 0
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
        # start = time.time()
        Engine1.MetaDeploy(Pattern)
        # print("serial took %.3f sec." % (time.time() - start))
        # 功率测量
        power = GetPower(streamer, args, chan)
        PowerMap[row, column] = power  # 模拟数据增量流入，保存历史数据3

print("acquire signal Power took %.3f sec." % (time.time() - start))

# mat_path = 'F:/zht/CCC/CCCcloseData/analys/through_wall_Position_Cal/2442_outside4.mat'
mat_path = 'C:/Users/admin/Desktop/CCC_laptop/RobotLocation/2442_outside2.mat'
io.savemat(mat_path, {'Outside1': PowerMap})


fig, (ax0, ax1) = plt.subplots(1, 2)
Z = PowerMap
Z = np.flip(Z, axis=1)
c = ax0.pcolor(Z, cmap='jet')
ax0.set_title('default: no edges')
c = ax1.pcolor(Z, edgecolors='k', linewidths=0.4)
ax1.set_title('thick edges')
fig.tight_layout()
plt.show()

fig2 = plt.figure()
plt.pcolor(Z.T, cmap='jet')
plt.colorbar(shrink=.83)
plt.xticks()
plt.yticks()
