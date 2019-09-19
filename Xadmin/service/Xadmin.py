from django.conf.urls import url
from django.shortcuts import HttpResponse,render,redirect
from django.urls import reverse
from django.utils.safestring import  mark_safe
from Xadmin.utils.page import Pagination
from django.db.models import Q
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.related import ManyToManyField
class show_list(object):
    def __init__(self,config,data,request):

        """
        # config字段为传进来的modelconfig类
        data为界面要展示的数据

        """
        self.config=config
        self.data=data
        self.request=request
        all_count=self.data.count()
        current_page=int(request.GET.get('page',1))
        path=request.path
        self.page=Pagination(current_page,all_count,path,request.GET,per_page_num=2, pager_count=12,)#分页器
        self.per_page_list=self.data[self.page.start:self.page.end]#Python内置的@property装饰器就是负责把一个方法变成属性调用的：
        #展示页面的表头部分
    def show_header(self):
        # thead
        header_list = []
        for list in self.config.new_list_display():
            if isinstance(list, str):#判断list_display中的字段是否是一个字符串，如果是，直接返回字段名称或者是对应的verbose_name
                if list == '__str__':#判断是否是__str__，如果没有添加自定义list_display字段的话，默认__str__
                    verbose_name = '名称'
                else:
                    verbose_name = self.config.model._meta.get_field(list).verbose_name  # 获取字段名中的verbose_name
            else:
                verbose_name = list(self.config, is_header=True)#如果是个操作的话，例如deit和delete，直接拿到当前循环的字段就是函数地址，加（）和参数直接调用拿到返回值
            header_list.append(verbose_name)#将以上的表头各项数据放在一个列表里，待模板使用
        return header_list
#展示表格主体
    def show_body(self):
        # tbody
        data_list = []
        for item in self.per_page_list:#self.per_page_list为分页之后的每页展示结果的数量
            tmp = []
            for field in self.config.new_list_display():
                if isinstance(field, str):#判断list_display中的字段是否是一个字符串，如果是，通过getattr拿到当前model类的对应的属性值

                    var_obj=self.config.model._meta.get_field(field)
                    if isinstance(var_obj,ManyToManyField):

                        temp=var_obj.remote_field.model.objects.all()
                        print("obj_ddd===========", tmp)
                        temp_list=[]
                        for item in temp:
                            print(item)
                            temp_list.append(str(item))

                        var=",".join(temp_list)
                    else:
                        var = getattr(item, field)
                    print('var_obj=================',var_obj)
                    if not self.config.list_display_links:#判断是否有list_display_links，如果是空的话跳过
                        pass
                    else:#如果ist_display_links不为空，则将当前编辑操作的a标签绑定在ist_display_links里的字段展示上，比如有了name字段的话，不会出现编辑那一栏的操作，而是通过点击name栏直接跳转
                        if field in self.config.list_display_links:
                            app_name = self.config.model._meta.app_label#获取app名字
                            model_name = self.config.model._meta.model_name#获取model名称
                            _url = reverse('%s_%s_change' % (app_name, model_name), args=(item.pk,))#利用反射查找对应的url
                            var = mark_safe('<a href="%s">%s</a>' % (_url, var))#mark_safe将生成的a标签直接再页面展示，相当于模板的safe，避免转义成字符串
                else:#如果不是一个list_display字段不是一个字符串，直接调用方法获得返回值
                    var = field(self.config, obj=item)
                tmp.append(var)
            data_list.append(tmp)
        return data_list
# 显示分页
    def show_page(self):
        _page=self.page.page_html()
        return _page
#获取filter中的各类选项
    def get_filter_list(self):

        # print("rel...",filter_field_obj.rel.to.objects.all())
        # if isinstance(filter_field_obj, ForeignKey) or isinstance(filter_field_obj, ManyToManyField):
        #     data_list = filter_field_obj.rel.to.objects.all()  # 【publish1,publish2...】
        import copy
        field_content = {}
        for filter_field in  self.config.filter_fields:#self.config.filter_fields过滤字段
            params = copy.deepcopy(self.request.GET)
            """"
            # 深copy，指向不同内存地址，以便后续对params的修改
            #如果params放在第一个for 循环外头，会导致第二次的filter_field拿到的request.GET与最初发过来的不同
            #比如刚开始循环的时候，params和request.GET是一样的，但是经过一轮删改之后，就变得不一样，如过此时继续对params进行修改，那么得到的后续a标签
            #中的href中的url是不对的，因为要想对每个a标签生成正确的url，每次循环必须是对当前访问的request.GEt进行操作。
            #这个bug找了很长时间，所以着重点写一下，下面的一个if循环中也会着重解释以下为啥会params=request.GET要放在第一个循环里边
            """

            field=self.config.model._meta.get_field(filter_field)
            """
             # print(field)#与教程中的不一样，找的时候注意用__dict__
             #教程中用的是data_list = filter_field_obj.rel.to.objects.all()
            #python 中预置的__dict__属性，是保存类实例或对象实例的属性变量键值对字典
            """

            if isinstance(field,ManyToManyField) or isinstance(field,ForeignKey):#判断当前字段是否是外键和对对多字段，因为取值的方式不一样
                data_list=field.remote_field.model.objects.all()
                # print('datalist===================',data_list)
            else:#普通字段，比如title，name
                data_list=field.model.objects.all()
            temp = []
            if params.get(filter_field):#如果GET中的url中已有当前循环的键值，删去，不然会造成？publish=1&publish=1现象
                del params[filter_field]
                #选择在此判断下对all的a标签进行生成，举个例子：
                """
                当前访问的url为?publish=2&author=2
                假设循环的字段顺序为publish，author
                当第一轮循环开始时，params为request.GET，所以PUBLISH下的all生成的标签会含有？author=2，因为你不知道用户接下来的筛选条件是啥，所以要保留后续author=2
                当第二轮循环开始时，params重新被赋值request.GET，所以AUTHOR下的all生成的标签会含有？publish=2，因为你不知道用户接下来的筛选条件是啥，所以要保留后续publish=2
                接上面的回答，如果params=request.GET放在循环外边，那么第一次循环结束之后，无论如何，params中已经有一个publish=2的键值，假设用户在展示界面先选择publish=2&author=2
                当用户点击PUBLISH下的all时此时进来这个判断时第一次循环request.GTE中是没有publish键值的，但是经过后续循环，使得params中有了一个publish=2的键值对，当第二轮循环时的时候
                就会给AUTHOR下的所有a标签都加上publish=2的键值
                """
                temp.append("<a href='?%s'>全部</a>" % params.urlencode())
            else:
                temp.append("<a  class='alive' href='#'>全部</a>")

            for item in data_list:#给a标签加正确的href属性
                pk =item.pk
                print(pk,'pk=====')
                text = str(item)
                if isinstance(field, ManyToManyField) or isinstance(field, ForeignKey):#如果是特殊字段取pk
                    params[filter_field] = pk
                else:#普通字段取内容，因为不存在title=pk值的书籍，只存在title='张昕宇是真的菜'的书籍
                    params[filter_field]=text
                _url=params.urlencode()
                if self.request.GET.get(filter_field)== str(pk) or self.request.GET.get(filter_field)== text:
                    #判断当前循环的键的值是否相匹配，如果匹配的话，说明用户点击了此标签，要加一个alive的class来区别未选中的
                    temp.append('<a class="alive" href="?%s">%s</a>'%(_url,text))
                else:#判断当前循环的键的值是否相匹配，如果不匹配的话，说明用户没有点击此标签
                    temp.append('<a  href="?%s">%s</a>' % (_url, text))
            field_content[filter_field]=temp

        return field_content

class ModelXadmin(object):
    list_display=["__str__"]
    list_display_links=[]
    search_fileds=[]
    filter_fields=[]

    def batch_deletion(self,request,queryset):
        queryset.delete()
    batch_deletion.action_name='批量删除'
    actions_fileds=[]
    def __init__(self,model,site):
        self.model=model
        self.site=site
#add  url获取
    def get_add_url(self):
        app_name = self.model._meta.app_label
        model_name = self.model._meta.model_name
        _url = reverse('%s_%s_add' % (app_name, model_name))  # arg后边要加‘，’+
        return _url

    # delete  url获取
    def get_edit_url(self,obj):

        app_name = self.model._meta.app_label
        model_name = self.model._meta.model_name
        _url = reverse('%s_%s_delete' % (app_name, model_name),args=(obj.pk))  # arg后边要加‘，’+
        return _url

    # edit  url获取
    def get_change_url(self,obj):
        app_name = self.model._meta.app_label
        model_name = self.model._meta.model_name
        _url = reverse('%s_%s_change' % (app_name, model_name),args=(obj.pk))  # arg后边要加‘，’+
    #list url
    def get_list_url(self):
        app_name = self.model._meta.app_label
        model_name = self.model._meta.model_name
        _url = reverse('%s_%s_list' % (app_name, model_name))  # arg后边要加‘，’+
        return _url
    #获取modelform  用来生成添加和编辑页面的表单
    def get_model_class(self):
        from django.forms import ModelForm

        class ModelFormDemo(ModelForm):
            class Meta:
                model = self.model
                fields = '__all__'

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                print('********',self.fields)
                for field in self.fields.values():
                    if 'DateField' in str(type(field)):
                        field.widget.attrs.update(
                            {"class": "form-control", "style": "margin-bottom:15px;", "type": "data"})
                    else:
                        field.widget.attrs.update({"class": "form-control", "style": "margin-bottom:15px;"})
        return ModelFormDemo
    #获取当前自定义config类的action
    def get_actions_list(self):
        tmp=[]
        if self.actions_fileds:
            for item in self.actions_fileds:
                #{"name":'batch_deletion','action':batch_deletion.action_name},{'name':'batch_edition','action':batch_edition.action_name}
                tmp.append(
                    {
                        'name':item.__name__,
                        'action':item.action_name
                    }
                )

        return tmp

    # 获取父类的action和子类中的action
    def get_new_actions_list(self):
        tmp=[]
        tmp.append(
            {
                'name':ModelXadmin.batch_deletion,
                'action':ModelXadmin.batch_deletion.action_name
            }
        )
        tmp.extend(self.get_actions_list())
        return tmp


    #按照当前自定义类的search字段进行Q操作结合成一个查询条件，比如当前search字段为title和name，将得到的查询值用Q连接成一个or操作，返回search_q，主函数filter字段以便查询
    def get_search(self,request):

        search_q = Q()
        search_q.connector = "or"#定义链接操作，默认是and
        if request.method == 'GET':
            self.keyword = request.GET.get('q', "")
            for item in self.search_fileds:
                search_q.children.append((item + '__contains', self.keyword))  # 注意是（）内加一个元组，里边再放两个值，字段名加_contains是模糊查找
        # print('search________________',search_q)>>>search________________ (or: ('title__contains', '张昕宇'), ('price__contains', '张昕宇'))
        return search_q

    # 按照当前自定义类的search字段进行Q操作结合成一个查询条件，比如当前filter为红旗出版社下张昕宇出版的书籍，此时过滤条件为且操作，需要返回一个and的filter_q，让list函数通过filter查询得到筛选的数据
    def get_filter(self,request):
        filter_q = Q()
        for key,value in request.GET.items():
            if key in self.filter_fields:
                filter_q.children.append((key,value))
        # if request.method == 'GET':
        #     for item in self.filter_fields:
        #         tmp=request.GET.get(item,"")
        #         print(tmp)
        #         filter_q.children.append((item,tmp))  # 注意是（）内加一个元组，里边再放两个值，
        # print(filter_q)
        return filter_q

    #编辑操作显示，list_display，每个model都会展示的部分，放在父类中不需要自定义也可以展示出来
    def edit(self,is_header=False,obj=None):
        if is_header:
            return '编辑'
        app_name = self.model._meta.app_label
        model_name = self.model._meta.model_name

        _url=reverse('%s_%s_change'%(app_name,model_name),args=(obj.pk,))#arg后边要加‘，’
        print('_url=============',_url)
        return mark_safe('<a href="%s">编辑</a>'%_url)

    # 删除操作显示，list_fileds，每个model都会展示的部分，放在父类中不需要自定义也可以展示出来
    def deletes(self,is_header=False,obj=None):
        if is_header:
            return '删除'
        app_name = self.model._meta.app_label
        model_name = self.model._meta.model_name

        _url=reverse('%s_%s_delete'%(app_name,model_name),args=(obj.pk,))#arg后边要加‘，’
        return mark_safe('<a href="%s">删除</a>'%_url)

    # 复选框操作显示，list_fileds，每个model都会展示的部分，放在父类中不需要自定义也可以展示出来
    def checkbox(self,is_header=False,obj=None):
        if is_header:
            return mark_safe('<input type="checkbox"  id="select_all">')#表头没有传obj对象
        return mark_safe('<input type="checkbox" name="selected" class="select_single" value="%s">'%obj.pk)
    #获取自定义的list_display和父类里的list_display字段
    def new_list_display(self):
        tmp=[]
        #如果换成self的话会出现以下错误
        # checkbox()
        # got
        # multiple
        # values
        # for argument 'is_header'
        tmp.append(ModelXadmin.checkbox)
        tmp.extend(self.list_display)
        if not self.list_display_links:
            tmp.append(ModelXadmin.edit)
        tmp.append(ModelXadmin.deletes)
        return tmp
    #展示页面
    def list_view(self,request):
        if request.method=="POST":
            action = request.POST.get('actions')#action
            operation_datas=request.POST.getlist('selected')#所选中的要批量修改的id
            if action:#判断返回的是否有值，如果是--------------返回的是NONE
                operate=getattr(self,action)
                queryset=self.model.objects.filter(pk__in=operation_datas)
                operate(request,queryset)

        filter_q=self.get_filter(request)
        search_q=self.get_search(request)
        data = self.model.objects.all().filter(search_q).filter(filter_q)
        showlist=show_list(self,data,request)
        add_url=self.get_add_url()
        return render(request,'list_view.html',locals())
#添加页面
    def add_view(self,request):
        ModelFormDemo=self.get_model_class()
        if request.method == 'POST':
            modelform = ModelFormDemo(request.POST)
            if modelform.is_valid():
                obj=modelform.save()
                if request.GET.get('id_response'):#判断是正常打开的add页面还是pop出来的，post请求也可以通过get获取？后边的参数
                    pk=obj.pk
                    text=str(obj)
                    id=request.GET.get('id_response')
                    print(id)
                    return render(request,'pop.html',locals())#给pop页面传入所需要的值，pop再传给他的父窗口，即add，这样就可以在pop关闭的时候在多选框那里添加上刚选中的值

                return redirect(self.get_list_url())
        else:
            modelform = ModelFormDemo()
            #给pop '+' 添加必要的属性
            for field in modelform:
                from django.forms.models import ModelChoiceField
                #为每个一对多或多对多的字段加一个‘+’

                if isinstance(field.field,ModelChoiceField):

                    model_name=field.field.queryset.model._meta.model_name
                    app_name=field.field.queryset.model._meta.app_label
                    _url=reverse('%s_%s_add'%(app_name,model_name))
                    #反向生成+的url
                    field.is_pop_flag=True
                    #设置一个标志位，如果为True，则渲染+
                    field.pop_url=_url+'?id_response=id_'+field.name

        return render(request, 'add_view.html',locals())






#编辑页面
    def change_view(self,request,nid):
        item=self.model.objects.filter(pk=nid).first()
        ModelForm = self.get_model_class()
        if request.method == 'POST':
            modelform=ModelForm(request.POST,instance=item)
            if modelform.is_valid():
                modelform.save()
                return redirect(self.get_list_url())
        else:
            modelform=ModelForm(instance=item)

        return render(request, 'change_view.html',locals())
#删除页面
    def delete_view(self,request,nid):
        return render(request, 'delete_view.html')

    def get_urls2(self):
        temp = []
        #反向查询时会用到，要保证每个url  name的唯一性，所以app_name+model_name可以确保唯一性
        app_name=self.model._meta.app_label
        model_name=self.model._meta.model_name
        temp.append(url(r"^$", self.list_view,name='%s_%s_list'%(app_name,model_name)))
        temp.append(url(r"^add/$", self.add_view,name='%s_%s_add'%(app_name,model_name)))
        temp.append(url(r"^(\d+)/change/$", self.change_view,name='%s_%s_change'%(app_name,model_name)))
        temp.append(url(r"^(\d+)/delete/$", self.delete_view,name='%s_%s_delete'%(app_name,model_name)))
        return temp

    @property
    def urls2(self):
        return self.get_urls2(), None, None

#此部分详解见admin插件流程txt
class Xadminsite(object):
    def __init__(self, name='Xadmin'):
        self._registry = {}  # model_class class -> admin_class instance
        self.name = name


    def register(self, model, admin_class=None, **options):
        if not admin_class:
                 admin_class = ModelXadmin

        self._registry[model] = admin_class(model, self) # {Book:ModelAdmin(Book),Publish:ModelAdmin(Publish)}


    def get_urls(self):

        tmp=[]
        for model,model_class_obj in self._registry.items():
            app_name=model._meta.app_label
            model_name=model._meta.model_name

            tmp.append(url(r'^{0}/{1}/'.format(app_name,model_name),model_class_obj.urls2),)
        return tmp


    @property
    def urls(self):
        return self.get_urls(),None,None

site=Xadminsite()