from config import *


class ResponseProtocol(object):
    """"服务器响应协议的格式化字符串处理"""

    @staticmethod
    def response_login_result(result, nickname, username):
        """"
        生成用户登录的结果字符串
        result: 表示登录成功与否
        nickname: 登录用户的昵称
        username: 登录用户的账号
        return: 供返回给用户的登录结果协议字符串
        """
        return DELIMITER.join([RESPONSE_LOGIN_RESULT, result, nickname, username])

    @staticmethod
    def response_chat(nickname, messages):
        """"
        生成返回给用户的消息字符串
        nickname: 发送消息的用户昵称
        messages: 消息正文
        return: 返回给用户的消息字符串
        """
        return DELIMITER.join([RESPONSE_CHAT, nickname, messages])

    @staticmethod
    def response_sign_up(result, username, nickname):
        """
        生成返回给用户的注册信息
        :param result: 表示注册成功或失败
        :param username: 用户账号
        :param nickname: 用户昵称
        :return: 拼接信息
        """
        return DELIMITER.join([RESPONSE_SIGN_UP, result, username, nickname])
