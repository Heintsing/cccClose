import numpy as np
import math


class EmTxRx:
    # 初始化 接收机和发射机参数
    def __init__(self, Location_Channel):
        # 发射机属性
        self.Xs = Location_Channel[0]
        self.Ys = Location_Channel[1]
        self.Zs = Location_Channel[2]  # 以正中心为原点
        self.E_s = 1
        self.Phi_s = 0 / 180 * math.pi
        # 接收机属性
        if Location_Channel[3] != np.nan:
            self.Xr = Location_Channel[3]
            self.Yr = Location_Channel[4]
            self.Zr = Location_Channel[5]
        else:
            self.Xr = 0
            self.Yr = 0
            self.Zr = 0



class MetaSurface(EmTxRx):
    # 初始化
    def __init__(self, Location_Channel, UnitNum):
        super(MetaSurface, self).__init__(Location_Channel)
        # 工作频率
        self.Freq = 2.442e9
        # 真空常量
        self.u = 4 * math.pi * 1e-7
        self.w = (1 / 36 / math.pi) * 1e-9
        self.c = 3e8
        self.k = 2 * math.pi * self.Freq * (self.w * self.u) ** 0.5
        # 超材料单元大小
        self.L_MetaUnit = 0.054
        self.UnitNum = UnitNum  # 超材料单元边长数目
        # 聚焦平面属性
        self.ReceivePlaneL = 2
        self.N_Cell_RecPlan = 100
        self.L_FocusUnit = self.ReceivePlaneL / self.N_Cell_RecPlan

    def GetMatePattern(self):
        # 超材料表面场值 EMonMateSurface
        X_matesurface = np.ones([1, self.UnitNum]).T * (self.L_MetaUnit * np.arange(1,self.UnitNum + 1) - self.L_MetaUnit / 2) - self.L_MetaUnit * self.UnitNum / 2
        Y_matesurface = (self.L_MetaUnit * np.arange(1, self.UnitNum + 1).reshape(self.UnitNum, 1) - self.L_MetaUnit / 2) * np.ones([1, self.UnitNum]) - self.L_MetaUnit * self.UnitNum / 2
        Z_matesurface = np.zeros([self.UnitNum, self.UnitNum])
        Smn = np.zeros([self.UnitNum, self.UnitNum], dtype=complex)
        Rns = np.sqrt(np.square(self.Xs - X_matesurface) + np.square(self.Ys - Y_matesurface) + np.square(self.Zs))  # 点源距离超材料的距离
        Rnr = np.sqrt(np.square(self.Xr - X_matesurface) + np.square(self.Yr - Y_matesurface) + np.square(self.Zr))  # 接收机距离超材料的距离
        Smn = np.multiply(self.E_s * 1 / Rns, np.exp(1j * self.k * Rns) * np.exp(1j * self.Phi_s))
        # def GetMetaPattern(self):
        # 量化
        self.Smn_hat = np.sign(np.cos(self.k * Rns + self.k * Rnr + self.Phi_s))

        # # def EMonFocusPlane(self):
        # Localx = np.ones([1, self.N_Cell_RecPlan]).T * (self.L_FocusUnit * np.arange(1, self.N_Cell_RecPlan + 1) - self.L_FocusUnit / 2 - self.ReceivePlaneL / 2)
        # Localy = (self.L_FocusUnit * np.arange(1, self.N_Cell_RecPlan + 1).reshape(self.N_Cell_RecPlan, 1) - self.L_FocusUnit / 2 - self.ReceivePlaneL / 2) * np.ones([1, self.N_Cell_RecPlan])
        # Z_FocusPoint = np.ones([self.N_Cell_RecPlan, self.N_Cell_RecPlan]) * self.Zr
        # X_FocusPoint = Localx
        # Y_FocusPoint = Localy
        #
        # # 聚焦点的场强
        # signalWithNoisePlane = np.zeros([self.N_Cell_RecPlan, self.N_Cell_RecPlan], dtype=complex)  # 1bit
        # signal = np.zeros([self.N_Cell_RecPlan, self.N_Cell_RecPlan], dtype=complex)  # 理想
        #
        # for a in range(0, self.N_Cell_RecPlan-1):
        #     for b in range(0, self.N_Cell_RecPlan-1):
        #         Rnr_ab_focus = np.sqrt(np.square(X_matesurface - X_FocusPoint[a, b]) + (Y_matesurface - Y_FocusPoint[a, b]) ** 2 + (Z_matesurface - Z_FocusPoint[a, b]) ** 2)  # 聚焦点距离超材料的距离
        #         # 目标主分量
        #         signal_ab = 2 / np.pi * np.exp(1j * self.Phi_s) * sum(sum(1 / Rnr / Rns * np.exp(1j * self.k * (-Rnr_ab_focus + Rnr))))
        #         # 根据量化单元值直接求解的 目标主分量 + 信号项
        #         signalWithNoisePlane[a, b] = sum(sum(self.Smn_hat * np.exp(-1j * self.k * (Rnr_ab_focus + Rns)) / Rnr_ab_focus / Rns))
        #         signal[a, b] = signal_ab
        #
        # self.ABS_1bit_EMPlane = signalWithNoisePlane

    def GetMatePatternMIMO(self, width):
        # 超材料表面场值 EMonMateSurface
        X_matesurface = np.ones([1, self.UnitNum]).T * (self.L_MetaUnit * np.arange(1,self.UnitNum + 1) - self.L_MetaUnit / 2) - self.L_MetaUnit * self.UnitNum / 2
        Y_matesurface = (self.L_MetaUnit * np.arange(1, self.UnitNum + 1).reshape(self.UnitNum, 1) - self.L_MetaUnit / 2) * np.ones([1, self.UnitNum]) - self.L_MetaUnit * self.UnitNum / 2
        Z_matesurface = np.zeros([self.UnitNum, self.UnitNum])
        Smn = np.zeros([self.UnitNum, self.UnitNum], dtype=complex)
        Rns = np.sqrt(np.square(self.Xs - X_matesurface) + np.square(self.Ys - Y_matesurface) + np.square(self.Zs))  # 点源距离超材料的距离
        Rnr1 = np.sqrt(np.square(self.Xr+width - X_matesurface) + np.square(self.Yr+width - Y_matesurface) + np.square(self.Zr))  # 接收机距离超材料的距离
        Rnr2 = np.sqrt(np.square(self.Xr-width - X_matesurface) + np.square(self.Yr+width - Y_matesurface) + np.square(self.Zr))  # 接收机距离超材料的距离
        Rnr3 = np.sqrt(np.square(self.Xr+width - X_matesurface) + np.square(self.Yr-width - Y_matesurface) + np.square(self.Zr))  # 接收机距离超材料的距离
        Rnr4 = np.sqrt(np.square(self.Xr-width - X_matesurface) + np.square(self.Yr-width - Y_matesurface) + np.square(self.Zr))  # 接收机距离超材料的距离
        Rnr0 = np.sqrt(np.square(self.Xr - X_matesurface) + np.square(self.Yr - Y_matesurface) + np.square(self.Zr))  # 接收机距离超材料的距离
        Smn = np.multiply(self.E_s * 1 / Rns, np.exp(1j * self.k * Rns) * np.exp(1j * self.Phi_s))
        # def GetMetaPattern(self):
        # 量化
        self.Smn_hat = np.sign(np.cos(self.k * Rns + self.k * Rnr0) +
                               np.cos(self.k * Rns + self.k * Rnr1) +
                               np.cos(self.k * Rns + self.k * Rnr2) +
                               np.cos(self.k * Rns + self.k * Rnr3) +
                               np.cos(self.k * Rns + self.k * Rnr4) +
                                      self.Phi_s)
