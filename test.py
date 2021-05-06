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