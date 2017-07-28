# coding=utf-8
__author__ = 'newdefence@164.com'
__date__ = "2017/7/26 上午1:09:00"

from tornado.gen import coroutine
from tornado.web import HTTPError, RequestHandler


class WeixinLoginHandler(RequestHandler):
    """用户微信登录（待开发）
    """
    def get(self, *args, **kwargs):
        pass


class PhoneLoginHandler(RequestHandler):
    """用户手机号登陆，需要使用验证码，返回 用户信息和 token
    """
    def get(self, *args, **kwargs):
        pass


class FollowHandler(RequestHandler):
    """关注/取消关注相关逻辑，全部使用 post 方式
    """
    def post(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        pass
