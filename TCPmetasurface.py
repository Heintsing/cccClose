import socket
import struct
import time
import os
from SerialPort import *
from focus import *
import numpy as np
from matplotlib import pyplot as plt


def TcpConnect():
    # 1. 创建tcp的套接字
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 2. 链接服务器
    tcp_socket.connect(("10.1.1.10", 7))
    # server_ip =  input("请输入要链接的服务器的ip:")
    # server_port = int(input("请输入要链接的服务器的port:"))
    # server_addr = (server_ip, server_port)
    # tcp_socket.connect(server_addr)
    print("Tcp connection successful!")
    return tcp_socket


def TcpsSend(tcp_socket):
    # 3. 发送数据/接收数据
    # send_data = input("请输入要发送的数据:")
    send_data = '0'
    tcp_socket.send(send_data.encode("utf-8"))


def TcpClose(tcp_socket):
    # 4. 关闭套接字
    tcp_socket.close()


def TcpsReceive(tcp_socket):
    recv_data = tcp_socket.recv(1024)
    print(recv_data)


# 复位指令--------------------------------------------------------------------------------------------
def OnReset():
    global tcp_socket
    lnSendLen = 20
    btResetCmdBuf = [0x5A, 0x5A, 0x5A, 0x5A, 0x00, 0x00, 0x00, 0x00, 0x5A, 0x5A,
                     0x5A, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A, 0x0E, 0x0F, 0x0F, 0x0F]
    btUnResetCmdBuf = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5A, 0x5A,
                       0x5A, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A, 0x0E, 0x0F, 0x0F, 0x0F]
    tx = ""
    for i in range(0, len(btResetCmdBuf)):
        btResetCmdBuf[i] = chr(btResetCmdBuf[i])
        tx = tx + btResetCmdBuf[i]
        # tcp_socket.send(btResetCmdBuf[i].encode("utf-8"))
        # print(btResetCmdBuf[i])
    tcp_socket.send(tx.encode("utf-8"))
    # 延时1秒
    time.sleep(1)
    tx = ""
    for i in range(0, len(btUnResetCmdBuf)):
        btUnResetCmdBuf[i] = chr(btUnResetCmdBuf[i])
        tx = tx + btUnResetCmdBuf[i]
        # tx = tx + btUnResetCmdBuf[i].encode("utf-8")
    tcp_socket.send(tx.encode("utf-8"))
    # print(btUnResetCmdBuf[i])


# 复位指令------------------------------------------------------------------------------------------
# 模式二只要发送完一次数据就会自动切换。
def OnResetMod2(m_PRFdata, tcp_socket):
    print("Reseting...")
    # global tcp_socket
    lnSendLen = 20
    btResetCmdBuf = [0x5A, 0x5A, 0x5A, 0x5A, 0x00, 0x00, 0x00, 0x00, 0x5A, 0x5A,
                     0x5A, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A, 0x0E, 0x0F, 0x0F, 0x0F]
    btUnResetCmdBuf = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5A, 0x5A,
                       0x5A, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A, 0x0E, 0x0F, 0x0F, 0x0F]
    tx = ""
    for i in range(0, len(btResetCmdBuf)):
        btResetCmdBuf[i] = chr(btResetCmdBuf[i])
        tx = tx + btResetCmdBuf[i]
        # tcp_socket.send(btResetCmdBuf[i].encode("utf-8"))
        # print(btResetCmdBuf[i])
    tcp_socket.send(tx.encode("utf-8"))
    # 延时1秒
    time.sleep(1)
    # -----------------------输入m_PRFdata-----------------------------
    # m_PRFdata = 1000000
    # -----------------------------------------------------------------

    if (m_PRFdata < 80):
        print("CPU重频过快")
    elif (m_PRFdata > 2147483647):
        print("CPU重频过慢")
    else:
        lnSendLen = 20
        # btStartCmdBuf = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        #                  0x00, 0x00, 0x5B, 0x5B, 0x5B, 0x5B, 0x00, 0x00, 0x00, 0x00]
        btStartCmdBuf = '00 00 00 00 '

        # 4\5\6\7位转为ASCII码形式(unsigned char)
        # btStartCmdBuf[4] = '0x{:02X}'.format(int((m_PRFdata-1)%256))
        a = '0x{:02X}'.format(int((m_PRFdata - 1) % 256))
        a = a[2:]
        btStartCmdBuf = btStartCmdBuf + a
        # if btStartCmdBuf[4] > 127: # 因为python中没有char类型，需要进行转换
        #     btStartCmdBuf[4] = btStartCmdBuf[4]-256
        a = '0x{:02X}'.format(int(((m_PRFdata - 1) % 65536) / 256))
        a = a[2:]
        btStartCmdBuf = btStartCmdBuf + ' ' + a
        a = '0x{:02X}'.format(int(((m_PRFdata - 1) % 16777216) / 65536))
        a = a[2:]
        btStartCmdBuf = btStartCmdBuf + ' ' + a
        a = '0x{:02X}'.format((int((m_PRFdata - 1) / 16777216)))
        a = a[2:]
        btStartCmdBuf = btStartCmdBuf + ' ' + a + ' ' + '5A 5A 5A 5A 5A 5A 5A 5A 0E 0F 0F 0F'
        print(btStartCmdBuf)
        tcp_socket.send(bytes.fromhex(btStartCmdBuf))
    print("Reset over")


# 停止指令--------------------------------------------------------------------------------------------
def OnStop():
    global tcp_socket
    lnSendLen = 20
    btStopCmdBuf = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A]
    tx = ""
    for i in range(0, len(btStopCmdBuf)):
        btStopCmdBuf[i] = chr(btStopCmdBuf[i])
        tx = tx + btStopCmdBuf[i]
        # tcp_socket.send(btStopCmdBuf[i].encode("utf-8"))
        # print(btStopCmdBuf[i])
    tcp_socket.send(tx.encode("utf-8"))


# 发送数据--------------------------------------------------------------------------------------------
def OnPara():
    global tcp_socket
    strParaFileName = "C:\\Users\\admin\\Desktop\\li1w\\datazht.bin"
    lnSendLen = 98304
    btSendParaBuf = []
    fpPara = open(strParaFileName, "rt")
    filepath = 'C:\\Users\\admin\\Desktop\\li1w\\datazht.bin'
    binfile = open(filepath, 'rb')  # 打开二进制文件
    # size = os.path.getsize(filepath) #获得文件大小
    # print(size)
    for k in range(1024):
        data = binfile.read(lnSendLen)
        tcp_socket.send(data)
        # for i in range(lnSendLen):
        # num = struct.unpack('B', data)
        # asc = chr(num[0])
        # tcp_socket.send(chr(data[i]).encode("utf-8"))
        # print(asc)
        print(k)
    binfile.close()


def OnParaMod2():
    global tcp_socket
    strParaFileName = "C:\\Users\\admin\\Desktop\\li1w\\datazhtccc.bin"
    lnSendLen = 12288
    btSendParaBuf = []
    fpPara = open(strParaFileName, "rt")
    filepath = 'C:\\Users\\admin\\Desktop\\li1w\\datazhtccc.bin'
    binfile = open(filepath, 'rb')  # 打开二进制文件
    # size = os.path.getsize(filepath) #获得文件大小
    # print(size)
    for k in range(1):
        data = binfile.read(lnSendLen)
        tcp_socket.send(data)
        # for i in range(lnSendLen):
        # num = struct.unpack('B', data)
        # asc = chr(num[0])
        # tcp_socket.send(chr(data[i]).encode("utf-8"))
        # print(asc)
        print(k)
    binfile.close()


def OnPatternonTime(PatternHex):
    global tcp_socket
    lnSendLen = 98304
    btSendParaBuf = []

    # size = os.path.getsize(filepath) #获得文件大小
    # print(size)
    for k in range(1024):
        tcp_socket.send(PatternHex)
        # for i in range(lnSendLen):
        # num = struct.unpack('B', data)
        # asc = chr(num[0])
        # tcp_socket.send(chr(data[i]).encode("utf-8"))
        # print(asc)
        print(k)


def OnPatternMod2onTime(PatternHex, tcpHandle):
    # global tcp_socket
    lnSendLen = 12288
    btSendParaBuf = []

    # size = os.path.getsize(filepath) #获得文件大小
    # print(size)
    for k in range(1):
        tcpHandle.send(PatternHex)
        # for i in range(lnSendLen):
        # num = struct.unpack('B', data)
        # asc = chr(num[0])
        # tcp_socket.send(chr(data[i]).encode("utf-8"))
        # print(asc)
        # print(k)


# 开始指令--------------------------------------------------------------------------------------------
# 只有模式1需要
def Onstart():
    global tcp_socket

    # -----------------------输入m_PRFdata-----------------------------
    m_PRFdata = 100
    # -----------------------------------------------------------------

    if (m_PRFdata < 80):
        print("CPU重频过快")
    elif (m_PRFdata > 2147483647):
        print("CPU重频过慢")
    else:
        lnSendLen = 20
        # btStartCmdBuf = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        #                  0x00, 0x00, 0x5B, 0x5B, 0x5B, 0x5B, 0x00, 0x00, 0x00, 0x00]
        btStartCmdBuf = '00 00 00 00 '

        # 4\5\6\7位转为ASCII码形式(unsigned char)
        # btStartCmdBuf[4] = '0x{:02X}'.format(int((m_PRFdata-1)%256))
        a = '0x{:02X}'.format(int((m_PRFdata - 1) % 256))
        a = a[2:]
        btStartCmdBuf = btStartCmdBuf + a
        # if btStartCmdBuf[4] > 127: # 因为python中没有char类型，需要进行转换
        #     btStartCmdBuf[4] = btStartCmdBuf[4]-256
        a = '0x{:02X}'.format(int(((m_PRFdata - 1) % 65536) / 256))
        a = a[2:]
        btStartCmdBuf = btStartCmdBuf + ' ' + a
        a = '0x{:02X}'.format(int(((m_PRFdata - 1) % 16777216) / 65536))
        a = a[2:]
        btStartCmdBuf = btStartCmdBuf + ' ' + a
        a = '0x{:02X}'.format((int((m_PRFdata - 1) / 16777216)))
        a = a[2:]
        btStartCmdBuf = btStartCmdBuf + ' ' + a + ' ' + '00 00 00 00 5B 5B 5B 5B 00 00 00 00'
        print(btStartCmdBuf)
        tcp_socket.send(bytes.fromhex(btStartCmdBuf))

# 3*3版本 模式1
def Image2hexTCP(M):  # 适配超材料的标准为3*3 24*32
    M = (M + 1) / 2
    # M = M.T
    M = np.flip(M, axis=1)
    M = np.concatenate((np.ones([8, 24]), M))
    # M = np.concatenate((M, np.ones([8, 24])))
    MM = np.concatenate((M[..., 0:8], M[..., 8:16], M[..., 16:24], M[..., 24:32]), axis=1).T
    # M = M.T
    # M = M.reshape(8, 8, 12)
    # MM = np.ones([96, 8], dtype=int)
    M = MM.reshape(96, 8).astype(np.int32)
    str1 = str(M)
    str1 = str1.replace('\n', '')
    str1 = str1.replace('[', '')
    # str1 = str1.replace(']', '')
    str1 = str1.replace(' ', '')
    str1 = str1.split(']')
    str1 = str1[0:96]
    Pattern = []
    for ii in range(0, int(str1.__len__())):
        CodeDec = str(int(str1[ii], 2))
        b = hex(int(CodeDec)).replace('0x', '')  # 16
        b = '{:0>2x}'.format(int(CodeDec))
        Pattern.append(b)
    Pattern = ''.join(Pattern) + ''
    Pattern = bytes.fromhex(Pattern)
    Pattern96128 = np.tile(Pattern, 1024)

    return Pattern96128

# 3*4版本 模式1
def Image2hex34TCP(M):  # 适配超材料的标准为3*3 24*32
    MM = np.copy(M.T)
    MM[0:8, 0:8] = np.rot90(MM[0:8, 0:8], -1)
    MM[0:8, 8:16] = np.rot90(MM[0:8, 8:16], -1)
    MM[0:8, 16:24] = np.rot90(MM[0:8, 16:24], -1)
    MM[0:8, 24:32] = np.rot90(MM[0:8, 24:32], -1)
    MM[8:16, 0:8] = np.rot90(MM[8:16, 0:8], -1)
    MM[8:16, 8:16] = np.rot90(MM[8:16, 8:16], -1)
    MM[8:16, 16:24] = np.rot90(MM[8:16, 16:24], -1)
    MM[8:16, 24:32] = np.rot90(MM[8:16, 24:32], -1)
    MM[16:24, 0:8] = np.rot90(MM[16:24, 0:8], -1)
    MM[16:24, 8:16] = np.rot90(MM[16:24, 8:16], -1)
    MM[16:24, 16:24] = np.rot90(MM[16:24, 16:24], -1)
    MM[16:24, 24:32] = np.rot90(MM[16:24, 24:32], -1)
    # M = M.T
    # M = M.reshape(8, 8, 12)
    # MM = np.ones([96, 8], dtype=int)
    M = MM.reshape(96, 8).astype(np.int32)
    str1 = str(M)
    str1 = str1.replace('\n', '')
    str1 = str1.replace('[', '')
    # str1 = str1.replace(']', '')
    str1 = str1.replace(' ', '')
    str1 = str1.split(']')
    str1 = str1[0:96]
    Pattern = []
    for ii in range(0, int(str1.__len__())):
        CodeDec = str(int(str1[ii], 2))
        b = hex(int(CodeDec)).replace('0x', '')  # 16
        b = '{:0>2x}'.format(int(CodeDec))
        Pattern.append(b)
    Pattern = ''.join(Pattern) + ''
    Pattern = bytes.fromhex(Pattern)
    Pattern961024 = np.tile(Pattern, 1024)

    return Pattern961024

# 3*4版本 模式2
def Image2hex34TCPMod2(M):  # 适配超材料的标准为3*3 24*32
    MM = np.copy(M.T)
    MM = np.flip(MM, 1)
    MM[0:8, 0:8] = np.rot90(MM[0:8, 0:8], -1)
    MM[0:8, 8:16] = np.rot90(MM[0:8, 8:16], -1)
    MM[0:8, 16:24] = np.rot90(MM[0:8, 16:24], -1)
    MM[0:8, 24:32] = np.rot90(MM[0:8, 24:32], -1)
    MM[8:16, 0:8] = np.rot90(MM[8:16, 0:8], -1)
    MM[8:16, 8:16] = np.rot90(MM[8:16, 8:16], -1)
    MM[8:16, 16:24] = np.rot90(MM[8:16, 16:24], -1)
    MM[8:16, 24:32] = np.rot90(MM[8:16, 24:32], -1)
    MM[16:24, 0:8] = np.rot90(MM[16:24, 0:8], -1)
    MM[16:24, 8:16] = np.rot90(MM[16:24, 8:16], -1)
    MM[16:24, 16:24] = np.rot90(MM[16:24, 16:24], -1)
    MM[16:24, 24:32] = np.rot90(MM[16:24, 24:32], -1)
    # M = M.T
    # M = M.reshape(8, 8, 12)
    # MM = np.ones([96, 8], dtype=int)
    M = MM.reshape(96, 8).astype(np.int32)
    str1 = str(M)
    str1 = str1.replace('\n', '')
    str1 = str1.replace('[', '')
    # str1 = str1.replace(']', '')
    str1 = str1.replace(' ', '')
    str1 = str1.split(']')
    str1 = str1[0:96]
    Pattern = []
    for ii in range(0, int(str1.__len__())):
        CodeDec = str(int(str1[ii], 2))
        b = hex(int(CodeDec)).replace('0x', '')  # 16
        b = '{:0>2x}'.format(int(CodeDec))
        Pattern.append(b)
    Pattern = ''.join(Pattern) + ''
    Pattern = bytes.fromhex(Pattern)
    Pattern9664 = np.tile(Pattern, 64)

    return Pattern9664


if __name__ == "__main__":

    mod = 2
    m_PRFdata = 100

    UnitNumY =  32
    UnitNum = 24
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(("10.1.1.10", 7))
    print("Tcp connection successful!")
    Smn_hat_tempt_stand_all_on = np.ones([UnitNumY, UnitNum])
    Smn_hat_tempt_stand_all_off = np.zeros([UnitNumY, UnitNum])

    UnitNum = 24
    # com = 'COM5'
    Location_Channel = np.array([0.0, 0, 2.684, 0.0, 0, 3])
    # Engine1 = Communication(com, 115200, 0.5)
    MS = MetaSurface(Location_Channel, UnitNum)
    MS.GetMatePattern34()

    a = 0
    try:
        if mod == 2:

            OnResetMod2(m_PRFdata, tcp_socket)
            while(1):
                start = time.time()
                if a % 2 == 0:
                    print("Inputing Parameter...")
                    # Pattern_hex = Image2hex34TCPMod2((MS.Smn_hat + 1) / 2)
                    # Pattern_hex = Image2hex34TCPMod2(Smn_hat_tempt_stand_all_off)
                    Smn_hat_tempt_stand_all_on[:, 1:24:2] = 0
                    Pattern_hex = Image2hex34TCPMod2(Smn_hat_tempt_stand_all_on)
                    OnPatternMod2onTime(Pattern_hex, tcp_socket)
                    # OnParaMod2()
                    print("Input over")

                    # print("Operating...")
                    # time.sleep(0.009)  # 不知道为什么必须要加一个延时，否则发送的数据会出错。

                    recv_data = tcp_socket.recv(1024)
                    print('receive on', recv_data)
                    # time.sleep(1)
                    # Onstart()
                    # OnResetMod2()
                    # print("Over")
                    # time.sleep(5)
                    # OnStop()
                else:

                    print("Inputing Parameter...")
                    # Pattern_hex = Image2hex34TCPMod2((MS.Smn_hat + 1) / 2)
                    # Pattern_hex = Image2hex34TCPMod2(Smn_hat_tempt_stand_all_off)
                    Smn_hat_tempt_stand_all_off[:, 1:24:2] = 1
                    Pattern_hex = Image2hex34TCPMod2(Smn_hat_tempt_stand_all_off)
                    OnPatternMod2onTime(Pattern_hex, tcp_socket)
                    # OnPara()
                    print("Input over")

                    # print("Operating...")
                    # time.sleep(0.009)  # 不知道为什么必须要加一个延时，否则发送的数据会出错。
                    recv_data = tcp_socket.recv(1024)
                    print('receive off', recv_data)
                    # time.sleep(1)
                    # Onstart()
                    # OnResetMod2()
                    # print("Over")
                    # time.sleep(5)
                    # OnStop()
                a = a+1
                print('a', a)
                print("top epoch took %.3f sec." % (time.time() - start))

        else:
            print("Reseting...")
            OnReset()
            print("Reset over")

            print("Inputing Parameter...")
            # OnPara()  # 从文件

            Smn_hat_tempt_stand_all_on[:, 3:24:4] = 0
            Pattern_hex = Image2hex34TCP(Smn_hat_tempt_stand_all_on)# (MS.Smn_hat + 1) / 2
            OnPatternonTime(Pattern_hex)   # 根据编码优化

            print("Operating...")
            time.sleep(0.009)  # 不知道为什么必须要加一个延时，否则发送的数据会出错。
            Onstart()

            print("Over")
            time.sleep(5)
            # OnStop()
    except SystemExit:
        print("Error: 没有找到文件或读取文件失败")
        print("stop trans")
        time.sleep(1)
        tcp_socket.close()

    fig, ax = plt.subplots(1, 1)
    ax.pcolor(-MS.Smn_hat, cmap='jet', edgecolors='k', linewidths=0.4)
    plt.show()
    """if __name__ == "__main__":
        tcp_socket = TcpConnect()
        for i in range(1,10):
            TcpsSend(tcp_socket)
            TcpsReceive(tcp_socket)
        TcpClose(tcp_socket)
        main()"""
