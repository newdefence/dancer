# coding=utf-8
__author__ = 'defence.zhang@gmail.com'
__date__ = "2017/7/28 上午12:50:00"

from tornado_mysql.pools import Pool
from tornado_mysql.cursors import DictCursor

import config

config.DB_DANCER_CONFIG["cursorclass"] = DictCursor
DancerPool = Pool(config.DB_DANCER_CONFIG, max_open_connections=60)
