# from matplotlib import pyplot as plt
# import numpy as np
#
#
# Pattern = np.ones([24, 24])
#
#
# fig = plt.figure()
# plt.pcolor(Pattern, cmap='jet', edgecolors='k', linewidths=0.4)
# plt.colorbar(shrink=.83)
# plt.xticks()
# plt.yticks()
# plt.show()
#
# fig, (ax0, ax1) = plt.subplots(1, 2)
# Z = - MS.Smn_hat
# Z = np.flip(Z, axis=1)
# c = ax0.pcolor(Z, cmap='jet')
# c = ax1.pcolor(Z, edgecolors='k', linewidths=0.4)
# fig.tight_layout()
# plt.show()
#
# fig2,ax0 = plt.figure()
# plt.pcolor(Z.T, cmap='jet')
# plt.colorbar(shrink=.83)
# plt.xticks()
# plt.yticks()
# plt.show()

#
# while True:
#     try:
#         # sleep(0.5)
#         print("still recording")
#     except KeyboardInterrupt:
#         print("Ctrl+C pressed")
#         camera.stop_recording()
#         break

# from SerialPort import *
# com1 = 'COM3'
# com2 = 'COM6'
# UnitNum = 24
# Engine1 = Communication(com1, 115200, 0.5)
# Engine2 = Communication(com2, 115200, 0.5)
# Smn_hat_tempt = np.ones([UnitNum, UnitNum])
# Smn_hat_tempt1 = np.zeros([UnitNum, UnitNum])
# Pattern1 = Engine1.Image2hex(Smn_hat_tempt)
# Pattern2 = Engine1.Image2hex(Smn_hat_tempt1)
#
# Engine1.MetaDeploy(Pattern2)
# Engine2.MetaDeploy(Pattern2)

for num in range(0,101,2):
    print(num)