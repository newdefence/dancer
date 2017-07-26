# coding=utf-8
__author__ = 'newdefence@163.com'
__date__ = "2017/7/26 上午 00:59:00"

try:
    from v1 import config
except ImportError:
    print "please copy v1/config.online.py to v1/config.py and modify it correctly as your local config file..."
    exit()

import sys
reload(sys)
sys.setdefaultencoding("utf8")

import os.path

from tornado.ioloop import IOLoop
from tornado.log import app_log
from tornado.options import define, options, parse_command_line
from tornado.web import Application, StaticFileHandler, RequestHandler


define("port", default=8100, type=int, help="server listen port")
define("debug", default=True, type=bool, help="server run mode")

parse_command_line()

from v1 import login


def main():
    settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=False,
        debug=options.debug,
        autoescape=None,
    )

    handlers = [
        (r"/login", login.WeixinLoginHandler),

    ]
    if options.debug:
        handlers += [
            (r"/contribution/(.*)", StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "live/contribution/"), }),
            (r"/replace/(.*)", StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "replace/"), }),
        ]

    application = Application(handlers, **settings)
    application.listen(options.port, xheaders=True)
    app_log.warning("dancer@1.0 start at port: %s" % options.port)
    IOLoop.current().start()


if __name__ == '__main__':
    main()
