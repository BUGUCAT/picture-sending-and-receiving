import tkinter as tk
import tkinter.filedialog
import socket
from PIL import Image, ImageTk
import struct
import os


class CLIENT:
    def __init__(self):
        # 生成tk界面 app即主窗口
        self.app = tk.Tk()
        # 修改窗口titile
        self.app.title("上传图片")
        # 设置主窗口的大小和位置
        self.app.geometry("250x400+200+200")

        # 图片路径显示
        self.path = tk.StringVar()
        self.entry = tk.Entry(self.app, state='readonly', text=self.path, width=30)
        self.entry.pack()

        # 使用Label显示图片
        self.lableShowImage = tk.Label(self.app)
        self.lableShowImage.pack()

        # 选择图片的按钮
        self.buttonSelImage = tk.Button(self.app, text='选择图片', command=self.choose_pic)
        self.buttonSelImage.pack()
        # buttonSelImage.pack(side=tk.BOTTOM)

        # 服务器地址
        self.addr_label = tk.Label(self.app, text="服务器地址")
        self.addr_label.pack()
        self.addr_entry = tk.Entry(self.app)
        self.addr_entry.insert(0, "127.0.0.1")
        self.addr_entry.pack()

        # 服务器端口
        self.port_label = tk.Label(self.app, text="服务器端口")
        self.port_label.pack()
        self.port_entry = tk.Entry(self.app)
        self.port_entry.insert(0, "8000")
        self.port_entry.pack()

        # 发送按钮
        self.buttonSend = tk.Button(self.app, text='发送', command=self.send_and_receive)
        self.buttonSend.pack()

    # 启动客户端
    def run(self):
        self.app.mainloop()

    # 选择图片
    def choose_pic(self):
        path_ = tkinter.filedialog.askopenfilename()
        if path_:
            print("选中图片：" + path_)
            self.path.set(path_)
            img_open = Image.open(self.entry.get())
            img = ImageTk.PhotoImage(img_open.resize((200, 200)))
            # img = ImageTk.PhotoImage(img_open)
            self.lableShowImage.config(image=img)
            self.lableShowImage.image = img

    # 发送图片
    def send_and_receive(self):
        filepath = self.path.get()  # 获取已选择图片的地址
        if filepath == '':  # 若未选择图片，报错
            print('未选中图片')
        else:
            s = socket.socket()  # 创建socket对象
            host = '127.0.0.1'  # 设置本地主机
            port = 8000  # 设置端口号

            # 尝试连接服务器
            try:
                s.connect((host, port))
                print('连接服务器成功：({0}, {1})'.format(host, port))
            except Exception as e:
                print('服务器连接失败')
                return


            # mess = input('你将要对服务端做什么？').encode()
            # s.send(mess)
            # print('客户端收到啦'.format(s.recv(2048)))
            # s.close()

            # 向服务器发送图片
            try:
                fhead = struct.pack(b'128sq', bytes(os.path.basename(filepath), encoding='utf-8'),
                                    os.stat(filepath).st_size)  # 将xxx.jpg以128sq的格式打包
                s.send(fhead)
                fp = open(filepath, 'rb')  # 打开要传输的图片
                while True:
                    data = fp.read(1024)  # 读入图片数据
                    if not data:
                        print('发送完毕：{0}'.format(filepath))
                        break
                    s.send(data)  # 以二进制格式发送图片数据
            except Exception as e:
                # print('Data error')
                print('发送失败')
                print(e)
                return

            # 接收服务器的返回图片数据
            seq = 0     # 定义一个变量 seq 作为序号
            buffer = {}     # 缓冲区
            for i in range(5):
                fileinfo_size = struct.calcsize(b'128sq')
                buf = s.recv(fileinfo_size)  # 接收图片名
                if not buf:
                    break

                # 解析数据包头部的序号和文件名
                filename, filesize = struct.unpack(b'128sq', buf)
                seq_str, filename = filename.decode('utf-8').split('_', 1)
                filename = filename.strip('\x00')
                seq = int(seq_str)

                # 接收数据包并将其存储到缓冲区中
                data = b''
                while len(data) < filesize:
                    packet = s.recv(filesize - len(data))
                    if not packet:
                        break
                    data += packet
                buffer[seq] = data

                # 判断是否需要输出文件并更新期望的下一个序号
                while seq in buffer:
                    print('收到文件：', filename)
                    fp = open(os.path.join('data\\receive\\', filename), 'ab')
                    fp.write(buffer[seq])
                    fp.close()
                    del buffer[seq]
                    seq += 1

                # # print(filename)
                # fn = filename.decode().strip('\x00')
                # print('收到文件：{0}'.format(fn))
                # new_filename = os.path.join(r'data\\receive\\' + fn)
                # recvd_size = 0
                # fp = open(new_filename, 'wb')
                # while not recvd_size == filesize:
                #     if filesize - recvd_size > 1024:
                #         data = s.recv(1024)
                #         recvd_size += len(data)
                #     else:
                #         data = s.recv(1024)
                #         recvd_size = filesize
                #     fp.write(data)  # 写入图片数据
                # fp.close()

            s.close()
            print('断开连接')





            # # 连接服务器
            # try:
            #     s = socket.socket()
            #     # s.connect(('192.168.1.12', 8000))  # 自定义服务器IP和端口
            #     s.connect((self.addr_entry.get(), int(self.port_entry.get())))  # 获取用户输入的服务器地址与端口
            # except Exception as e:
            #     print('Connection error')
            #     print(e)
            #     s.close()
            #     return

            # # 发送图片
            # try:
            #     fhead = struct.pack(b'128sq', bytes(os.path.basename(filepath), encoding='utf-8'),
            #                         os.stat(filepath).st_size)  # 将xxx.jpg以128sq的格式打包
            #     s.send(fhead)
            #     fp = open(filepath, 'rb')  # 打开要传输的图片
            #     while True:
            #         data = fp.read(1024)  # 读入图片数据
            #         if not data:
            #             print('发送完毕：{0}'.format(filepath))
            #             break
            #         s.send(data)  # 以二进制格式发送图片数据
            # except Exception as e:
            #     # print('Data error')
            #     print('发送失败')
            #     print(e)
            #     return
            #
            # # 接收五张图片
            # try:
            #     # 接收服务器返回的响应
            #     response_data = b""
            #     while True:
            #         packet = s.recv(4096)
            #         if not packet:
            #             break
            #         response_data += packet
            #
            #     # 保存服务器返回的五张图片到本地
            #     for i in range(5):
            #         with open(f'data/gray_image_{i}.jpg', 'wb') as f:
            #             f.write(response_data[i * len(response_data) // 5:(i + 1) * len(response_data) // 5])
            # except Exception as e:
            #     pass
            # finally:
            #     s.close()


if __name__ == "__main__":
    client = CLIENT()
    client.run()
