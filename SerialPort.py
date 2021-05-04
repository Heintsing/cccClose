import serial
import serial.tools.list_ports
import numpy as np
import string
import binascii


class Communication():

    # 初始化
    def __init__(self, com, bps, timeout):
        self.port = com
        self.bps = bps
        self.timeout = timeout
        global Ret
        try:
            # 打开串口，并得到串口对象
            self.main_engine = serial.Serial(self.port, self.bps, timeout=self.timeout)
            # 判断是否打开成功
            if (self.main_engine.is_open):
                Ret = True
        except Exception as e:
            print("---异常---：", e)

    # 打印设备基本信息
    def Print_Name(self):
        print(self.main_engine.name)  # 设备名字
        print(self.main_engine.port)  # 读或者写端口
        print(self.main_engine.baudrate)  # 波特率
        print(self.main_engine.bytesize)  # 字节大小
        print(self.main_engine.parity)  # 校验位
        print(self.main_engine.stopbits)  # 停止位
        print(self.main_engine.timeout)  # 读超时设置
        print(self.main_engine.writeTimeout)  # 写超时
        print(self.main_engine.xonxoff)  # 软件流控
        print(self.main_engine.rtscts)  # 软件流控
        print(self.main_engine.dsrdtr)  # 硬件流控
        print(self.main_engine.interCharTimeout)  # 字符间隔超时

    # 打开串口
    def Open_Engine(self):
        self.main_engine.open()

    # 关闭串口
    def Close_Engine(self):
        self.main_engine.close()
        print(self.main_engine.is_open)  # 检验串口是否打开

    # 打印可用串口列表
    @staticmethod
    def Print_Used_Com():
        port_list = list(serial.tools.list_ports.comports())
        print(port_list)

    # 接收指定大小的数据
    # 从串口读size个字节。如果指定超时，则可能在超时后返回较少的字节；如果没有指定超时，则会一直等到收完指定的字节数。
    def Read_Size(self, size):
        return self.main_engine.read(size=size)

    # 接收一行数据
    # 使用readline()时应该注意：打开串口时应该指定超时，否则如果串口没有收到新行，则会一直等待。
    # 如果没有超时，readline会报异常。
    def Read_Line(self):
        return self.main_engine.readline()

    # 发数据
    def Send_data(self, data):
        self.main_engine.write(data)

    # 更多示例
    # self.main_engine.write(chr(0x06).encode("utf-8")) # 十六制发送一个数据
    # print(self.main_engine.read().hex()) # # 十六进制的读取读一个字节
    # print(self.main_engine.read())#读一个字节
    # print(self.main_engine.read(10).decode("gbk"))#读十个字节
    # print(self.main_engine.readline().decode("gbk"))#读一行
    # print(self.main_engine.readlines())#读取多行，返回列表，必须匹配超时（timeout)使用
    # print(self.main_engine.in_waiting)#获取输入缓冲区的剩余字节数
    # print(self.main_engine.out_waiting)#获取输出缓冲区的字节数
    # print(self.main_engine.readall())#读取全部字符。

    # 接收数据
    # 一个整型数据占两个字节
    # 一个字符占一个字节

    def Recive_data(self, way):
        # 循环接收数据，此为死循环，可用线程实现
        print("开始接收数据：")
        while True:
            try:
                # 一个字节一个字节的接收
                if self.main_engine.in_waiting:
                    if (way == 0):
                        for i in range(self.main_engine.in_waiting):
                            print("接收ascii数据：" + str(self.Read_Size(1)))
                            data1 = self.Read_Size(1).hex()  # 转为十六进制
                            data2 = int(data1, 16)  # 转为十进制
                            if (data2 == "exit"):  # 退出标志
                                break
                            else:
                                print("收到数据十六进制：" + data1 + " 收到数据十进制：" + str(data2))
                    if (way == 1):
                        # 整体接收
                        # data = self.main_engine.read(self.main_engine.in_waiting).decode("utf-8")#方式一
                        data = self.main_engine.read_all()  # 方式二
                        if (data == "exit"):  # 退出标志
                            break
                        else:
                            print("接收ascii数据：", data)
            except Exception as e:
                print("异常报错：", e)

    def Image2hex(self, M):
        M = (M + 1) / 2
        # M = M.T
        M=np.flip(M, axis=1)
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

        return Pattern
    def MetaDeploy(self,Pattern):
        # self.Send_data(chr(255).encode("utf-8"))
        headers = '7e 00'  # bytes.fromhex('7e 00')
        # tile = bytes.fromhex('7e')
        PatternEnd = Pattern.copy()
        PatternEnd[95] = '7e'
        Peroid = '7e ff ff' + ' ' + ' '.join(PatternEnd)  # bytes.fromhex('7e ff ff'+' '+' '.join(PatternEnd))
        PatternBit = headers+' '+' '.join(Pattern)+' '+'7e'+' '+Peroid

        # print(PatternBit[79])
        a = bytes.fromhex(PatternBit)
        # print(PatternBit)

        self.Send_data(bytes.fromhex(PatternBit))

if __name__ == "__main__":
    Communication.Print_Used_Com()
    Ret = False  # 是否创建成功标志

    Engine1 = Communication("com2", 115200, 0.5)
    # if Ret:
    #     Engine1.Recive_data(0)
    # Pattern = ' '.join(Pattern)
    # b = hex(int())
    # b = b.replace('0x','')
    # b.encode('ascii')
    # Engine1.Send_data(b.encode('ascii'))
    # Engine1.Send_data(chr(255).encode("utf-8"))
    Pattern = Engine1.Image2hex(np.ones([24,24]))
    headers = '7e 00'  # bytes.fromhex('7e 00')
    # tile = bytes.fromhex('7e')
    PatternEnd = Pattern.copy()
    PatternEnd[95] = '7e'
    Peroid = '7e ff ff'+' '+' '.join(PatternEnd)  # bytes.fromhex('7e ff ff'+' '+' '.join(PatternEnd))
    PatternBit = headers+' '+' '.join(Pattern)+' '+'7e'+' '+Peroid

    # d = bytes.fromhex('ff')
    Engine1.Send_data(bytes.fromhex(PatternBit))