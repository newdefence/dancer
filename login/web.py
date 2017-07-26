# coding=utf-8
__author__ = 'defence.zhang@gmail.com'
__date__ = "2017/07/27 23:10:00"

"""WEB方式授权登录（是否有用待定，copy旧的逻辑代码）
"""

from urlparse import parse_qs, urlparse

# from tornado.auth import OAuth2Mixin
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat, urlencode
from tornado.gen import coroutine, Return
from tornado.web import RequestHandler, HTTPError

from tornado.escape import url_escape

import v1.config as config


WEIBO_OAUTH_CALLBACK_URL = "http://www.waqu.com/member/login/weibo"
WEIBO_OAUTH_AUTHORIZE_URL = "https://api.weibo.com/oauth2/authorize"
WEIBO_OAUTH_ACCESS_TOKEN_URL = "https://api.weibo.com/oauth2/access_token"
WEIBO_OAUTH_CLIENT_ID = config.WEIBO_OAUTH_CLIENT_ID
WEIBO_OAUTH_CLIENT_SECRET = config.WEIBO_OAUTH_CLIENT_SECRET
WEIBO_OAUTH_SCOPE = []

WEIBO_LOGIN_URL = url_concat(WEIBO_OAUTH_AUTHORIZE_URL, {"client_id": WEIBO_OAUTH_CLIENT_ID, "response_type": "code", "redirect_uri": WEIBO_OAUTH_CALLBACK_URL})


# http://www.waqu.com/member/login/weibo?code=CODE
# http://open.weibo.com/wiki/OAuth2/access_token
# http://open.weibo.com/wiki/2/users/show
class WeiboOAuth2CallbackHandler(RequestHandler):
    @coroutine
    def get_authenticated_user(self, code):
        http, accessTokenConfig, userConfig = AsyncHTTPClient(), None, None
        # 1. 获取 AccessToken
        response = yield http.fetch(WEIBO_OAUTH_ACCESS_TOKEN_URL, body=urlencode({
            "client_id": WEIBO_OAUTH_CLIENT_ID, "client_secret": WEIBO_OAUTH_CLIENT_SECRET,
            "grant_type": "authorization_code", "redirect_uri": WEIBO_OAUTH_CALLBACK_URL, "code": code
        }), raise_error=False, request_timeout=5.0, connect_timeout=3.0, method="POST")
        # TODO 存储过期时间和 AccessToken
        # {"access_token": "SlAV32hkKG", "remind_in": 3600, "expires_in": 3600, "uid":"12341234"}
        if not response.error:
            try: accessTokenConfig = json_decode(response.body)
            except: pass
        if not accessTokenConfig: raise HTTPError(403)
        # 2. 获取 用户 Uid
        # 有的 API 上写的有 UID，有的需要单独请求申请 UID，真是醉了；
        # if "uid" not in accessTokenConfig:
        #     response = yield http.fetch(url_concat("https://api.weibo.com/2/account/get_uid.json", {
        #         "source": WEIBO_OAUTH_CLIENT_ID, "access_token": accessTokenConfig["access_token"]
        #     }), raise_error=False, request_timeout=5.0, connect_timeout=3.0, method="GET")
        #     uidConfig = json_decode(response.body)
        #     uid = uidConfig["uid"]
        # else: uid = accessTokenConfig["uid"]
        # 获取用户信息；
        # NOTE：首次登陆的用户，需要写入数据库
        response = yield http.fetch(url_concat("https://api.weibo.com/2/users/show.json", {
            "source": WEIBO_OAUTH_CLIENT_ID, "access_token": accessTokenConfig["access_token"], "uid": accessTokenConfig["uid"]
        }), raise_error=False, request_timeout=5.0, connect_timeout=3.0, method="GET")
        if not response.error:
            try: userConfig = json_decode(response.body)
            except: pass
        raise Return(userConfig)

    @coroutine
    def get(self, *args, **kwargs):
        code = self.get_query_argument("code", None)
        if not code:
            self.redirect(WEIBO_LOGIN_URL)
            return
        user = yield self.get_authenticated_user(code)
        if not user: raise HTTPError(403)
        self.finish(user)
        # TODO 存储过期时间和 AccessToken
        # {"access_token": "SlAV32hkKG", "remind_in": 3600, "expires_in": 3600}


QQ_OAUTH_CALLBACK_URL = "http://www.waqu.com/member/login/qq"
QQ_OAUTH_AUTHORIZE_URL = "https://graph.qq.com/oauth2.0/authorize"
QQ_OAUTH_ACCESS_TOKEN_URL = "https://graph.qq.com/oauth2.0/token"
QQ_OAUTH_CLIENT_ID = config.QQ_OAUTH_CLIENT_ID
QQ_OAUTH_CLIENT_SECRET = config.QQ_OAUTH_CLIENT_SECRET
QQ_OAUTH_SCOPE = []

QQ_LOGIN_URL = url_concat(QQ_OAUTH_AUTHORIZE_URL, {"client_id": QQ_OAUTH_CLIENT_ID, "response_type": "code", "redirect_uri": QQ_OAUTH_CALLBACK_URL, "state": "test"})


# QQ_WAP_OAUTH_AUTHORIZE_URL = "https://graph.z.qq.com/moc2/authorize"
# QQ_WAP_OAUTH_ACCESS_TOKEN_URL = "https://graph.z.qq.com/moc2/token"

# http://wiki.connect.qq.com/
# http://wiki.connect.qq.com/%E4%BD%BF%E7%94%A8authorization_code%E8%8E%B7%E5%8F%96access_token
# http://wiki.connect.qq.com/%E8%8E%B7%E5%8F%96%E7%94%A8%E6%88%B7openid_oauth2-0
# http://wiki.connect.qq.com/%E4%BD%BF%E7%94%A8authorization_code%E8%8E%B7%E5%8F%96access_token
# http://wiki.open.qq.com/wiki/website/get_user_info


class QQOAuth2CallbackHandler(RequestHandler):
    tmpAccessToken = None
    @coroutine
    def get_authenticated_user(self, code):
        http, accessTokenConfig, userConfig = AsyncHTTPClient(), None, None
        # 1. 获取 AccessToken
        response = yield http.fetch(url_concat(QQ_OAUTH_ACCESS_TOKEN_URL, {
            "client_id": QQ_OAUTH_CLIENT_ID, "client_secret": QQ_OAUTH_CLIENT_SECRET,
            "grant_type": "authorization_code", "redirect_uri": QQ_OAUTH_CALLBACK_URL, "code": code
        }), raise_error=False, request_timeout=5.0, connect_timeout=3.0, method="GET")
        # TODO 存储过期时间和 AccessToken
        # access_token=FE04************************CCE2&expires_in=7776000&refresh_token=88E4************************BE1
        if not response.error:
            try: accessTokenConfig = parse_qs(response.body)
            except: pass
        if not accessTokenConfig: raise HTTPError(403)
        # 2. 获取 用户 openid
        # 浏览器调用
        access_token = accessTokenConfig["access_token"][0]
        # callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} );
        self.finish("""
        <script>function callback(config){location.href = "?access_token=%s&client_id=" + config.client_id + "&openid=" + config.openid}</script>
        <script src="https://graph.qq.com/oauth2.0/me?access_token=%s"></script>
        """ % (access_token, access_token))

        # response = yield http.fetch("https://graph.qq.com/oauth2.0/me?access_token=%s" % accessTokenConfig["access_token"], raise_error=False, request_timeout=5.0, connect_timeout=3.0, method="GET")
        # if response.error: raise HTTPError(403)

    @coroutine
    def getQQUserInfo(self, openId, access_token):
        # 获取用户信息；
        # NOTE：首次登陆的用户，需要写入数据库
        http, accessTokenConfig, userConfig = AsyncHTTPClient(), None, None
        response = yield http.fetch(url_concat("https://graph.qq.com/user/get_user_info", {
            "oauth_consumer_key": QQ_OAUTH_CLIENT_ID, "access_token": access_token, "openid": openId, "format": "json"
        }), raise_error=False, request_timeout=5.0, connect_timeout=3.0, method="GET")
        if not response.error:
            try: userConfig = json_decode(response.body)
            except: pass
        raise Return(userConfig)

    @coroutine
    def get(self, *args, **kwargs):
        code = self.get_query_argument("code", None)
        if code:
            yield self.get_authenticated_user(code)
            return
        clientId, openId, userConfig = self.get_query_argument("client_id", None), self.get_query_argument("openid", None), None
        if clientId == QQ_OAUTH_CLIENT_ID and openId:
            userConfig = yield self.getQQUserInfo(openId, self.get_query_argument("access_token"))
        if userConfig:
            self.finish(userConfig)
            return
        if not clientId and not openId:
            self.redirect(QQ_LOGIN_URL)
            return
        raise HTTPError(404)


# https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1&id=open1419316505&token=f93d2cfff2515bc1a081814e0560924c03472dbe&lang=zh_CN
WEIXIN_OAUTH_CALLBACK_URL = "http://www.waqu.com/member/login/wechat"
WEIXIN_OAUTH_AUTHORIZE_URL = "https://open.weixin.qq.com/connect/qrconnect?"
WEIXIN_OAUTH_ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
WEIXIN_OAUTH_CLIENT_ID = config.WEIXIN_OAUTH_CLIENT_ID
WEIXIN_OAUTH_CLIENT_SECRET = config.WEIXIN_OAUTH_CLIENT_SECRET
WEIXIN_OAUTH_SCOPE = ["snsapi_login"]

WEIXIN_LOGIN_URL = url_concat(WEIXIN_OAUTH_AUTHORIZE_URL, {"appid": WEIXIN_OAUTH_CLIENT_ID, "response_type": "code", "redirect_uri": WEIXIN_OAUTH_CALLBACK_URL, "scope": ",".join(WEIXIN_OAUTH_SCOPE), "state": "test"}) + "#wechat_redirect"


class WeixinOAuth2CallbackHandler(RequestHandler):
    @coroutine
    def get_authenticated_user(self, code):
        http, accessTokenConfig, userConfig = AsyncHTTPClient(), None, None
        # 1. 获取 AccessToken
        response = yield http.fetch(url_concat(WEIXIN_OAUTH_ACCESS_TOKEN_URL, {
            "appid": WEIXIN_OAUTH_CLIENT_ID, "secret": WEIXIN_OAUTH_CLIENT_SECRET,
            "grant_type": "authorization_code", "code": code
        }), raise_error=False, request_timeout=5.0, connect_timeout=3.0, method="GET")
        # TODO 存储过期时间和 AccessToken
        # {"access_token": "ACCESS_TOKEN", "expires_in": 7200, "refresh_token": "REFRESH_TOKEN", "openid": "OPENID", "scope": "SCOPE", "unionid": "o6_bmasdasdsad6_2sgVt7hMZOPfL"}
        if not response.error:
            try: accessTokenConfig = json_decode(response.body)
            except: pass
        if not accessTokenConfig: raise HTTPError(403)
        # 2. 获取 用户 openid
        response = yield http.fetch(url_concat("https://api.weixin.qq.com/sns/userinfo", {"access_token": accessTokenConfig["access_token"], "openid": accessTokenConfig["openid"]}), raise_error=False, request_timeout=5.0, connect_timeout=3.0, method="GET")
        if response.error: raise HTTPError(403)
        try: userConfig = json_decode(response.body)
        except: pass
        raise Return(userConfig)


    @coroutine
    def get(self, *args, **kwargs):
        code, user = self.get_query_argument("code", None), None
        if code:
            user = yield self.get_authenticated_user(code)
        if user:
            self.finish(user)
            return
        self.redirect(WEIXIN_LOGIN_URL)
