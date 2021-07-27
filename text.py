# for a in range(1, 20):
import numpy as np

# b = np.ones(2, 10)
# print(b[1, 9])

# arr1=np.arange(10,20)
# arr2=np.arange(20,30)
# arr3=np.arange(20).reshape(4,5)
# arr4=np.arange(20).reshape(4,5)
# arr5=np.array([1,1,1,1,1])
# arr6=np.array([1,1,1,1])
#
# print(np.concatenate((arr1,arr2)))
# a=np.concatenate((arr3,arr4),axis=1)
# print(a)
# print(np.concatenate((arr3,arr4),axis=0))
#
# print(a[1,2])


# M = (np.ones([24, 24]) + 1) / 2
# M = np.concatenate((M, np.ones([8, 24])))
# M = np.concatenate((M[0:8], M[8:16], M[16:24], M[24:32]), axis=1)
# M = M.T
# M = M.reshape(8, 8, 12)
# MM = np.ones([96, 8], dtype=int)
# M = M.reshape(96, 8).astype(np.int32)
# str1 = str(M)
# str1 = str1.replace('\n', '')
# str1 = str1.replace('[', '')
# # str1 = str1.replace(']', '')
# str1 = str1.replace(' ', '')
# str1 = str1.split(']')
# str1 = str1[0:96]
# Pattern = []
# for ii in range(0,int(str1.__len__())):
#     Pattern.append(str(int(str1[ii], 2)))
# print(Pattern)


# import matplotlib.pyplot as plt
# import numpy as np
# import time
# from math import *
#
# plt.ion() #开启interactive mode 成功的关键函数
# plt.figure(1)
# t = [0]
# t_now = 0
# m = [sin(t_now)]
#
# for ii in range(1000):
#     plt.clf() #清空画布上的所有内容
#     t_now = ii*0.1
#     t.append(t_now)#模拟数据增量流入，保存历史数据
#     m.append(sin(t_now))#模拟数据增量流入，保存历史数据
#     plt.plot(t,m,'-r')
#     plt.draw()#注意此函数需要调用
#     # time.sleep(0.01)
#     plt.pause(0.01)


import numpy as np
from matplotlib import pyplot as plt

# x = np.arange(1, 11)
# y = 2 * x + 5
#
# Posi = np.zeros([1, 3])
# Posi = np.append(Posi, [[1, 1, 1]], axis=0)
# a = [1, 1, 1]
# a = np.array(a).reshape(-1, 3)
# Posi = np.append(Posi, a, axis=0)
#
# plt.title("Matplotlib demo")
# plt.xlabel("x axis caption")
# plt.ylabel("y axis caption")
# plt.plot(Posi, "ob")
#
#
# plt.show()
#
#
#
# for i in range(1,10):
#     print(i)


import numpy as np

# mat = np.array([[1, 3, 5],
#
#                 [2, 4, 6],
#
#                 [7, 8, 9]
#
#                 ])
# print(mat, "# orignal")
# mat90 = np.rot90(mat, -1)
#
# print(mat90, "# rorate 90 anti-clockwise")
Smn_hat_tempt_stand_all_on = np.ones([32, 24])
Smn_hat_tempt_stand_all_on[:, 0:24:4] = 0
print(Smn_hat_tempt_stand_all_on)
