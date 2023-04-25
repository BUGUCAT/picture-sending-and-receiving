import os
import socket
import socketserver, struct, gzip, time


def handle(path):
    # 此处为对path图片的分析处理过程
    # 处理完毕后得到五张最为相似的图片地址
    pic1 = r'data\\gallery\\pic1.jpeg'
    pic2 = r'data\\gallery\\pic2.jpeg'
    pic3 = r'data\\gallery\\pic3.jpg'
    pic4 = r'data\\gallery\\pic4.jpeg'
    pic5 = r'data\\gallery\\pic5.jpeg'
    return pic1, pic2, pic3, pic4, pic5


class SERVER():
    # 创建一个TCP套接字
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建socket对象
    host = '127.0.0.1'  # 设置本地主机
    port = 8000  # 设置端口
    s.bind((host, port))  # 绑定端口
    s.listen(5)  # 开始监听，等待客户连接

    def __init__(self):
        self.bufSize = 8388608  # 每一次接受的字节流长度

        while True:
            conn, addr = self.s.accept()  # 建立客户连接
            print("已连接：", addr)  # 打印发送端的ip和端口

            while True:
                fileinfo_size = struct.calcsize('128sq')
                buf = conn.recv(fileinfo_size)  # 接收图片名
                if buf:
                    filename, filesize = struct.unpack('128sq', buf)
                    fn = filename.decode().strip('\x00')
                    print('收到文件：{0}'.format(fn))
                    new_filename = os.path.join(r'data\\receive\\' + fn)
                    recvd_size = 0
                    fp = open(new_filename, 'wb')
                    while not recvd_size == filesize:
                        if filesize - recvd_size > 1024:
                            data = conn.recv(1024)
                            recvd_size += len(data)
                        else:
                            data = conn.recv(1024)
                            recvd_size = filesize
                        fp.write(data)  # 写入图片数据
                    fp.close()

                # 调用图片分析处理函数
                pics = handle(r'data\\receive\\' + fn)

                # 向客户端发送分析处理后得到的五张图片
                seq = 0  # 定义一个变量 seq 作为序号
                for pic_path in pics:
                    try:
                        seq += 1
                        fhead = struct.pack(b'128sq',
                                            bytes(str(seq) + '_' + os.path.basename(pic_path), encoding='utf-8'),
                                            os.stat(pic_path).st_size)  # 将xxx.jpg以128sq的格式打包
                        conn.send(fhead)
                        fp = open(pic_path, 'rb')  # 打开要传输的图片
                        while True:
                            data = fp.read(1024)  # 读入图片数据
                            if not data:
                                print('发送完毕：{0}'.format(pic_path))
                                break
                            conn.send(data)  # 以二进制格式发送图片数据
                    except Exception as e:
                        print('发送失败：' + pic_path)
                        print(e)
                        return

                conn.close()
                print('断开连接')
                break


if __name__ == "__main__":
    server = SERVER()
