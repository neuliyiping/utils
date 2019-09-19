from django.db import models

from Xadmin.service.Xadmin import site #引入site单例对象
#

from app01.models import *
from app02.models import *

site.register(Transactions)#使用register进行注册
site.register(Foodeat)#使用register进行注册