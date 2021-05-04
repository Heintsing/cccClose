import socket

def TcpConnect():
    # 1. 创建tcp的套接字
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 2. 链接服务器
    # tcp_socket.connect(("192.168.33.11", 7890))
    server_ip =  '192.168.3.11' #input("请输入要链接的服务器的ip:")
    server_port = 7890 #int(input("请输入要链接的服务器的port:"))
    server_addr = (server_ip, server_port)
    tcp_socket.connect(server_addr)
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


if __name__ == "__main__":
    tcp_socket = TcpConnect()
    for ii in range(1,10):
        TcpsSend(tcp_socket)
        TcpsReceive(tcp_socket)
    TcpClose(tcp_socket)
    # main()