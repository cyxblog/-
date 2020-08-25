from threading import Thread

from server_socket import ServerSocket
from socket_wrapper import SocketWrapper
from config import *
from response_protocol import *
from db import DB


class Server(object):
    """服务器核心类"""

    def __init__(self):
        # 创建服务器套接字
        self.server_socket = ServerSocket()

        # 创建请求的id和方法关联字典
        self.request_handle_function = {}
        self.register(REQUEST_LOGIN, self.request_login_handle)
        self.register(REQUEST_CHAT, self.request_chat_handle)
        self.register(REQUEST_SIGN_UP, self.request_sign_up_handle)

        # 创建保存当前用户登录字典
        self.clients = {}

        # 创建数据库管理对象
        self.db = DB()

    def register(self, request_id, handle_function):
        # 注册消息类型和处理函数到字典
        self.request_handle_function[request_id] = handle_function

    def startup(self):
        """获取客户端连接，提供服务"""
        while True:
            # 获取客户端连接
            print('正在获取客户端连接')
            soc, addr = self.server_socket.accept()
            print('获取到客户端连接')

            # 使用套接字生成包装对象
            client_soc = SocketWrapper(soc)

            # 收发消息
            t = Thread(target=self.request_handle, args=(client_soc,))
            t.start()

    def request_handle(self, client_soc):
        """处理客户端请求"""
        while True:
            recv_data = client_soc.recv_data()
            if not recv_data:
                self.remove_office_user(client_soc)
                client_soc.close()
                break
            print(recv_data)

            # 解析数据
            parse_data = self.parse_request_text(recv_data)

            # 分析请求类型，并根据类型调用相应函数

            handle_function = self.request_handle_function.get(parse_data['request_id'])
            if handle_function:
                handle_function(client_soc, parse_data)

    def remove_office_user(self, client_soc):
        # 客户端下线处理
        print('有客户端下线了')
        for username, info in self.clients.items():
            if info['sock'] == client_soc:
                print(self.clients)
                del self.clients[username]
                print(self.clients)
                break

    def parse_request_text(self, text):
        """"
        解析客户端发送来的数据
        登录信息：0001|username|password
        聊天信息：0002|username|messages
        注册信息：0003|username|password|nickname
        """
        print('解析客户端数据：' + text)
        request_list = text.split(DELIMITER)

        # 按照类型解析数据
        request_data = {}
        request_data['request_id'] = request_list[0]

        if request_data['request_id'] == REQUEST_LOGIN:
            # 用户登录信息
            request_data['username'] = request_list[1]
            request_data['password'] = request_list[2]

        elif request_data['request_id'] == REQUEST_CHAT:
            # 用户聊天信息
            request_data['username'] = request_list[1]
            request_data['messages'] = request_list[2]

        elif request_data['request_id'] == REQUEST_SIGN_UP:
            # 用户注册信息
            request_data['username'] = request_list[1]
            request_data['password'] = request_list[2]
            request_data['nickname'] = request_list[3]

        return request_data

    def request_chat_handle(self, client_soc, request_data):
        # 处理聊天功能
        print('收到聊天信息。。。准备处理', request_data)

        # 获取消息内容
        username = request_data['username']
        messages = request_data['messages']
        nickname = self.clients[username]['nickname']

        # 拼接发送给客户端的消息文本
        msg = ResponseProtocol.response_chat(nickname, messages)

        # 转发给在线用户
        for u_name, info in self.clients.items():
            if username == u_name:  # 不需要向发送消息的账号转发消息
                continue
            info['sock'].send_data(msg)

    def request_sign_up_handle(self, client_soc, request_data):
        # 处理注册功能
        print('收到注册请求。。。准备处理')
        # 获取密码
        username = request_data['username']
        password = request_data['password']
        nickname = request_data['nickname']

        # 检查是否能够注册
        ret, username, nickname = self.check_user_sign_up(username, nickname)

        # 注册成功将当前用户信息插入数据库
        if ret == '1':
            user_id = self.db.count_user()
            self.db.insert_user(
                "insert into users values(%d,'%s','%s','%s')" % (user_id + 1, username, password, nickname))

        # 拼接返回给客户端的信息
        response_text = ResponseProtocol.response_sign_up(ret, username, nickname)

        # 发送信息给客户端
        client_soc.send_data(response_text)

    def request_login_handle(self, client_soc, request_data):
        # 处理登录功能
        print('收到登录请求。。。准备处理')
        # 获取账号密码
        username = request_data['username']
        password = request_data['password']

        # 检查是否能够登录
        ret, nickname, username = self.check_user_login(username, password)

        # 登录成功保存当前用户
        if ret == '1':
            self.clients[username] = {'sock': client_soc, 'nickname': nickname}

        # 拼接返回给客户端的消息
        response_text = ResponseProtocol.response_login_result(ret, nickname, username)

        # 把消息发送给客户端
        client_soc.send_data(response_text)

    def check_user_login(self, username, password):
        """检查用户是否登录成功，并返回检查结果(0/失败，1/成功)，昵称，用户名"""
        # 从数据库查询用户信息
        result = self.db.get_one("select * from users where user_name='%s'" % username)

        # 没有查询结果则说明用户不存在，登录失败
        if not result:
            return '0', '', username

        # 如果密码不匹配，说明密码错误，登陆失败
        if password != result['user_password']:
            return '0', '', username

        # 登录成功
        return '1', result['user_nickname'], username

    def check_user_sign_up(self, username, nickname):
        """检查用户是否注册成功，并返回检查结果(0/失败，1/成功)，昵称，用户名"""
        # 从数据库查询用户信息
        username_result = self.db.search_one("select * from users where user_name='%s'" % username)
        nickname_result = self.db.search_one("select * from users where user_nickname='%s'" % nickname)

        # 有相同账号则注册失败
        if username_result:
            return '0', username, ''

        # 有相同昵称则注册失败
        elif nickname_result:
            return '0', '', nickname

        # 注册成功
        return '1', username, nickname


if __name__ == '__main__':
    Server().startup()
