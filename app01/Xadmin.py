from Xadmin.service.Xadmin import site #引入site单例对象
from app01.models import *
from Xadmin.service.Xadmin import ModelXadmin
from django.urls import reverse
from django.utils.safestring import  mark_safe
class BookConfig(ModelXadmin):

    # list_display=['__str__']
    list_display = ['title', "price", 'publish','authors']
    list_display_links=['title']
    search_fileds=['title','price']

    def batch_edition(self,request,queryset):
        queryset.update(price=100)
    batch_edition.action_name='批量改价'
    actions_fileds=[batch_edition]

    filter_fields=['title','publish','authors']

site.register(Book,BookConfig)#使用register进行注册
site.register(Publish)#使用register进行注册
site.register(Author)#使用register进行注册
site.register(AuthorDetail)#使用register进行注册