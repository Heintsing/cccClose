from scipy.io import loadmat
from SerialPort import *
from matplotlib import pyplot as plt

com1 = 'COM8'  # 天花板
com2 = 'COM7'  # 竖着的

PatternSavePath = r"C:\Users\admin\Desktop\CCC_laptop\CCCans\收发同时优化后编码\采集数据用\位置低\Smn_hat_record1.mat"
Smn_hat_stand = loadmat(PatternSavePath)
Smn_hat_stand = Smn_hat_stand["Smn_hat_record"]
a = Smn_hat_stand[6][:][:]
b = Smn_hat_stand[7][8:32][:]
Engine2 = Communication(com2, 115200, 0.5)
Engine2.Print_Name()
fig, (ax, ax1) = plt.subplots(1, 2)
ax.pcolor(a, cmap='jet', edgecolors='k', linewidths=0.4)
ax1.pcolor(b, cmap='jet', edgecolors='k', linewidths=0.4)
print(a)
plt.show()

Pattern_up = Engine2.Image2hex(b)
Pattern_stand = Engine2.Image2hex34(a)
Bit_up = Engine2.MetaDeployMultiPattern(Pattern_up, 0)
Bit_stand = Engine2.MetaDeployMultiPattern(Pattern_stand, 0)
fo = open("2424联合在线优化编码_位置低20210707.txt", "wb")
print ("文件名为: ", fo.name)
str = "菜鸟教程"
fo.write(Bit_up)
fo = open("3224联合在线优化编码_位置低20210707.txt", "wb")
print ("文件名为: ", fo.name)
str = "菜鸟教程"
fo.write(Bit_stand)