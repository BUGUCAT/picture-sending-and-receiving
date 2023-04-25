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
        self.app.geometry("400x600+200+200")

        # 左右两部分框架
        self.left_frame = tk.Frame(self.app, width=250, height=400)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_frame = tk.Frame(self.app, width=150, height=400)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 图片路径显示
        self.path = tk.StringVar()
        self.entry = tk.Entry(self.left_frame, state='readonly', text=self.path, width=30)
        self.entry.pack()

        # 使用Label显示图片
        self.labelShowImage = tk.Label(self.left_frame)
        self.labelShowImage.pack()

        # 选择图片的按钮
        self.buttonSelImage = tk.Button(self.left_frame, text='选择图片', command=self.choose_pic)
        self.buttonSelImage.pack()
        # buttonSelImage.pack(side=tk.BOTTOM)

        # 服务器地址
        self.addr_label = tk.Label(self.left_frame, text="服务器地址")
        self.addr_label.pack()
        self.addr_entry = tk.Entry(self.left_frame)
        self.addr_entry.insert(0, "127.0.0.1")
        self.addr_entry.pack()

        # 服务器端口
        self.port_label = tk.Label(self.left_frame, text="服务器端口")
        self.port_label.pack()
        self.port_entry = tk.Entry(self.left_frame)
        self.port_entry.insert(0, "8000")
        self.port_entry.pack()

        # 发送按钮
        self.buttonSend = tk.Button(self.left_frame, text='发送', command=self.send_and_receive)
        self.buttonSend.pack()

        # 状态显示
        self.status_label = tk.Label(self.left_frame)
        self.status_label.pack()

        # 服务器回传图片显示
        self.pic_label = tk.Label(self.right_frame, text="结果", width=15)
        self.pic_label.pack()
        self.labelResultImage1 = tk.Label(self.right_frame)
        self.labelResultImage2 = tk.Label(self.right_frame)
        self.labelResultImage3 = tk.Label(self.right_frame)
        self.labelResultImage4 = tk.Label(self.right_frame)
        self.labelResultImage5 = tk.Label(self.right_frame)
        self.labelResultImage1.pack()
        self.labelResultImage2.pack()
        self.labelResultImage3.pack()
        self.labelResultImage4.pack()
        self.labelResultImage5.pack()
        self.arr = {0: self.labelResultImage1, 1: self.labelResultImage2, 2: self.labelResultImage3,
                    3: self.labelResultImage4, 4: self.labelResultImage5}

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
            self.labelShowImage.config(image=img)
            self.labelShowImage.image = img

    # 发送图片
    def send_and_receive(self):
        filepath = self.path.get()  # 获取已选择图片的地址
        if filepath == '':  # 若未选择图片，报错
            print('未选中图片')
        else:
            s = socket.socket()  # 创建socket对象
            host = self.addr_entry.get()  # 设置本地主机
            port = int(self.port_entry.get())  # 设置端口号

            # 尝试连接服务器
            try:
                s.connect((host, port))
                print('连接服务器成功：({0}, {1})'.format(host, port))
            except Exception as e:
                print('服务器连接失败')
                self.status_label.config(text='服务器连接失败')
                return

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
                        self.status_label.config(text='发送完毕')
                        break
                    s.send(data)  # 以二进制格式发送图片数据
            except Exception as e:
                # print('Data error')
                print('发送失败')
                print(e)
                return

            # 接收服务器的返回图片数据
            seq = 0  # 定义一个变量 seq 作为序号
            buffer = {}  # 缓冲区
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

                # 将收到的图片显示在页面上
                pic = Image.open(os.path.join('data\\receive\\', filename))
                img = ImageTk.PhotoImage(pic.resize((100, 100)))
                self.arr[i].config(image=img)
                self.arr[i].image = img

            self.status_label.config(text='接收完成')
            s.close()
            print('断开连接')


if __name__ == "__main__":
    client = CLIENT()
    client.run()
