# coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core import serializers
from .forms import *
from .help import *
from zhiwu.models import *
import json
import time
import os
# Create your views here.


success = {"code": 1}
fail = {"code": 0}


def home(request):
    return render(request, "index.html")


# def home(request):
#     # room = ManagerForm()
#     r = {"user": 2, "kk":3}
#     # return HttpResponseRedirect("admin_manager")
#
#     return render(request, "detail.html", {"r": json.dumps(r)})
#     # return HttpResponse("hello world",status=200)

def test(request):
    room = RoomPicture.objects.all()
    return render(request, "home.html", {'rooms': json.dumps(serializers.serialize('json', room))})


def check_root(request):
    try:
        user = request.session.get('user')
        status = request.session.get('status')
        if status == 'root':
            return True, user, status
        else:
            return False, None, None
    except Exception, e:
        print 'check root error:'
        print e
        return False, None, None


def check_manager(request):
    try:
        user = request.session.get('user')
        status = request.session.get('status')
        if status == 'manager':
            return True, user, status
        else:
            return False, None, None
    except Exception, e:
        print 'check root error:'
        print e
        return False, None, None




def search(request):
    return render(request, "search.html")


def work_search(request):
    distance = {"walk": {"10": 0.010, "15": 0.015, "30": 0.030},
                "bus": {"10": 0.02, "15": 0.025, "30": 0.050},
                "drive": {"10": 0.03, "15": 0.050, "30": 0.100}}
    time_get = request.GET.get("time", None)
    way = request.GET.get("way", None)
    longitude = request.GET.get("lng", None)
    latitude = request.GET.get("lat", None)
    if time is None or way is None or longitude is None and latitude is None:
        return HttpResponseNotFound()
    else:
        try:
            dis = distance.get(way).get(time_get)
        except:
            return HttpResponseNotFound()
        if dis is None:
            return HttpResponseNotFound()
        rooms = RoomInfo.objects.filter(lng__range=(longitude - dis, longitude + dis),
                                        lat__range=(latitude - dis, latitude + dis))
        room_list = get_search_room_list(rooms)
        return render(request, "search.html", {"rooms": room_list})


def home_search(request):
    # home_location
    # longitude = models.FloatField(default=120.200)
    # latitude = models.FloatField(default=30.3)
    location = request.GET.get("home_location", None)
    longitude = request.GET.get("lng", None)
    latitude = request.GET.get("lat", None)
    # rooms = Room.objects.filter(community=location)
    rooms = RoomInfo.objects.all()
    dis = 0.010
    if len(rooms) == 0:
        rooms = RoomInfo.objects.filter(longitude__range=(longitude - dis, longitude + dis),
                                        latitude__range=(latitude - dis, latitude + dis))
    room_list = get_search_room_list(rooms)
    # room_list = serializers.serialize('json', room_list)
    return render(request, "search.html", {"rooms": json.dumps(room_list)})


def map_search(request):
    # longitude = models.FloatField(default=120.200)
    # latitude = models.FloatField(default=30.3)
    longitude_l = request.GET.get("lng_left", None)
    latitude_l = request.GET.get("lat_left", None)
    longitude_r = request.GET.get("lng_right", None)
    latitude_r = request.GET.get("lat_right", None)
    rooms = Room.objects.filter(longitude__range=(longitude_l, longitude_r),
                                latitude__range=(latitude_l, latitude_r))
    room_list = get_search_room_list(rooms)
    return JsonResponse(room_list)


def room_detail(request):
    try:
        roomNum = request.GET.get('roomNumber')
        room = RoomInfo.objects.get(roomNumber=roomNum)
        #cp = SecondManager.objects.get(user=room.contactPerson)
        #cp = []
        roomP = get_room_picture(room)
        return render(request, "detail.html", {"room": room,
                                               "picture": roomP})
    except Exception, e:
        print e
        return HttpResponseNotFound()


def admin_manager_login(request):
    if request.method == "POST":
        form = AdminLogin(request.POST)
        if form.is_valid():
            try:
                user = form.cleaned_data['login_user']
                pw = form.cleaned_data['login_pw']
                status = form.cleaned_data['login_type']
                if status == "manager":
                    tag, m = get_manager(user, pw)
                elif status == "second_manager":
                    tag, m = get_second_manager(user, pw)
                elif status == "root":
                    request.session['user'] = "root"
                    request.session['status'] = "root"
                    return HttpResponseRedirect("admin_manager/")
                    # todo 完善root的数据库
                else:
                    return HttpResponse(status=-1)
                    # 身份不正确
                if tag:
                    request.session['user'] = m.user
                    request.session['status'] = m.status
                    if m.status == "manager":
                        return HttpResponseRedirect("admin_manager/")
                    else:
                        return HttpResponseRedirect("admin_second_manager/")
                else:
                    return HttpResponse(status=0)
                    # 账号密码错误
            except Exception, e:
                print e
    return render(request, "manager_login.html")


def admin_login(request):
    return render(request, "index.html")


def admin_root(request):
    status = request.session.get("status", "")
    user = request.session.get("user", "")
    if is_root(status):
        m_list = get_manager_list()
        community_list = get_community_list()
        return render(request, "backend.html", {"managers": m_list,
                                                "status": status,
                                                "user": user,
                                                "communities": community_list})
    else:
        return HttpResponseRedirect(reverse("manager_login"))


def admin_manager(request):
    managerget = request.GET.get("manager", "")
    status = request.session.get("status", "")
    user = request.session.get("user", "")
    if is_manager(status):
        mu = request.session.get("user", "")
    elif is_root(status) and managerget != "":
        mu = managerget
    else:
        return HttpResponseRedirect(reverse("manager_login"))
    try:
        manager = Manager.objects.get(user=mu)
    except:
        # return HttpResponseRedirect(reverse("manager_login"))
        return render(request, "backendL1.html")
    m_list = get_second_manager_list(manager)
    return render(request, "backendL1.html", {"second_managers": m_list,
                                              "status": status,
                                              "user": user})


def admin_second_manager(request):
    secondmanagerget = request.GET.get("second_manager", "")
    status = request.session.get("status", "")
    user = request.session.get("user", "")
    if is_second_manager(status):
        smu = request.session.get("user", "")
    elif (is_root(status) or is_manager(status)) and secondmanagerget != "":
        smu = secondmanagerget
    else:
        return HttpResponseRedirect(reverse("manager_login"))
    rooms = Room.objects.filter(contactPerson=smu)
    return render(request, "backendL2.html", {"rooms": rooms,
                                              "status": status,
                                              "user": user})


def new_house(request):
    user = request.session.get("user")
    status = request.session.get("status", "")
    # sm=SecondManager.objects.get(user=user)
    # communities = Community.objects.filter(manager=sm.manager)
    if is_second_manager(status):
        return render(request, "newHouse.html", {"user": user,
                                                 "status": status,})
                                                 # "communities": communities})
    else:
        return HttpResponseRedirect(reverse("manager_login"))


def client_back(request):
    return render(request, "clientBackend.html")


def client_back_account(request):
    return render(request, "myAccount.html")


def client_back_list(request):
    return render(request, "mylist.html")


def client_back_comment(request):
    return render(request, "serviceContact.html")


def room_collection(request):
    return render(request, "")


# post
# JianDing

def post_area_search(request):
    try:
        return manager_search(request, 'area')
    except Exception, e:
        print e
        return JsonResponse(fail)


def post_mansion_manager_search(request):
    try:
        return manager_search(request, 'mansion')
    except Exception, e:
        print e
        return JsonResponse(fail)


def manager_search(request, status):
    district = request.GET.get('manager_search_district', "")
    m_list = Manager.objects.filter(district__icontains=district,
                                    status = status)
    result = {'code': 1,
              'context': serializers.serialize('json', m_list)}
    return JsonResponse(result, safe=False)


def post_get_manager_search(request):
    try:
        user = request.GET.get('id')
        m = Manager.objects.get(user=user)
        result = {'code': 1,
                  'context': {'user': m.user,
                              'pw': m.pw,
                              'name': m.name,
                              'phone': m.phone,
                              'status': m.status,
                              'district': m.district,
                              'exist': m.exist}}
        return JsonResponse(result)
    except Exception, e:
        print e
        return JsonResponse(fail)


def post_get_second_manager_search(request):
    try:
        user = request.GET.get('id')
        m = SecondManager.objects.get(user=user)
        result = {'code': 1,
                  'context': {'manager': m.manager.user,
                               'user': m.user,
                               'pw': m.pw,
                               'name': m.name,
                               'phone': m.phone,
                               'company': m.company,
                               'status': m.status,
                               'exist': m.exist}}
        return JsonResponse(result)
    except Exception, e:
        print e
        return JsonResponse(fail)


def post_get_community_list_by_manager(request):
    try:
        manager = request.GET.get('id')
        c_list = Community.objects.filter(manager=manager)
        c_list = serializers.serialize('json', c_list)
        result = {'code': 1,
                  'context': c_list}
        return JsonResponse(result, safe=False)
    except Exception, e:
        print 'post_get_community_list_by_manager error:'
        print e
        return JsonResponse(fail)


def post_get_community(request):
    try:
        name = request.GET.get('id')
        c = Community.objects.get(name=name)
        result = {'code': 1,
                  'context': {'name': c.name,
                              'manager': c.manager,
                              'item': c.item,
                              'lng': c.lng,
                              'lat': c.lat,
                              'area': c.area,
                              'district': c.district,
                              'business': c.business,
                              'keyword': c.keyword,
                              'type': c.type,
                              'year': c.year,
                              'level': c.level,
                              'facility': c.facility,
                              'green': c.green,
                              'security': c.security}}
        return JsonResponse(result)
    except Exception, e:
        print e
        return JsonResponse(fail)


def post_area_add_or_modify(request):
    return post_manager_add_or_modify(request, "area")


def post_mansion_manager_add_or_modify(request):
    return post_manager_add_or_modify(request, "mansion")


# code from here
def post_manager_add_or_modify(request, status):
    if request.method == 'POST':  # 当提交表单时
        form = ManagerForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            try:
                user = form.cleaned_data['manager_account']
                pw = form.cleaned_data['manager_pw']
                name = form.cleaned_data['manager_name']
                phone = form.cleaned_data['manager_phone']
                district = form.cleaned_data['manager_district']
                p = manager_add_or_modify(user, pw, name, phone, status, district)
                if p:
                    return JsonResponse(success)
                else:
                    return JsonResponse(fail)
            except Exception, e:
                print e
                return JsonResponse(fail)
        else:
            return JsonResponse(fail)
    else:  # 当正常访问时
        return HttpResponseNotFound()


# 添加或者修改一条一级管理员


# def post_manager_modify(request):
#     if request.method == 'POST':  # 当提交表单时
#         form = ManagerForm(request.POST)  # form 包含提交的数据
#         if form.is_valid():  # 如果提交的数据合法
#             try:
#                 user = form.cleaned_data['manager_account']
#                 pw = form.cleaned_data['manager_pw']
#                 name = form.cleaned_data['manager_name']
#                 phone = form.cleaned_data['manager_phone']
#                 status = form.cleaned_data['manager_status']
#                 district = form.cleaned_data['manager_district']
#                 p = manager_modify(user, pw, name, phone, status, district)
#                 return HttpResponse(status=1)
#             except Exception, e:
#                 print e
#                 return HttpResponse(status=0)
#     else:  # 当正常访问时
#         print 'not post'
# # 修改一条一级管理员


# def post_manager_create(request):
#     if request.method == 'POST':  # 当提交表单时
#         form = ManagerUserForm(request.POST)  # form 包含提交的数据
#         if form.is_valid():  # 如果提交的数据合法
#             try:
#                 user = form.cleaned_data['manager_account']
#                 p, flag = Manager.objects.get_or_create(user=user)
#                 if not flag:
#                     p.exist = True
#                 print 'create success!'
#                 return HttpResponse(status=1)
#             except Exception, e:
#                 print e
#                 return HttpResponse(status=0)
#     else:  # 当正常访问时
#         print 'not post'


# 创建一个空的一级管理员


def post_manager_delete(request):
    if request.method == 'POST':  # 当提交表单时
        form = ManagerUserForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            try:
                user = form.cleaned_data['id']
                p = manager_delete(user)
                if p:
                    print 'delete success!'
                    return JsonResponse(success)
                else:
                    return JsonResponse(fail)
            except Exception, e:
                print e
                return JsonResponse(fail)
        else:
            return JsonResponse(fail)
    else:  # 当正常访问时
        return HttpResponseNotFound()


# 删除一个一级管理员


# code from here
def post_manager_logout(request):
    if request.method == 'POST':  # 当提交表单时
        form = ManagerUserForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            user = form.cleaned_data['id']
            p = manager_logout(user)
            if p:
                return JsonResponse(success)
            else:
                return JsonResponse(fail)
        else:
            return JsonResponse(fail)
    else:
        return HttpResponseNotFound()
# 管理员登出


def post_manager_active(request):
    if request.method == 'POST':  # 当提交表单时
        form = ManagerUserForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            try:
                user = form.cleaned_data['id']
                p = manager_active(user)
                if p:
                    return JsonResponse(success)
                else:
                    return JsonResponse(fail)
            except Exception, e:
                print e
                return JsonResponse(fail)
        else:
            return JsonResponse(fail)
    else:
        print 'not post'
        return HttpResponseNotFound()
# 激活一个管理员账号


def post_manager_pw(request):
    if request.method == 'POST':
        form = ManagerPwdChange(request.POST)
        if form.is_valid():
            try:
                user = form.cleaned_data['manager_account']
                oldpw = form.cleaned_data['manager_oldpw']
                newpw = form.cleaned_data['manager_newpw']
                p = manager_pw(user, oldpw, newpw)
                return HttpResponse(status=1)
            except Exception, e:
                print e
                return HttpResponse(status=0)
    else:
        print 'not post'


def mansion_keeper_add_or_modify(request):
    return post_second_manager_add_or_modify(request, 'mansion')


def wuye_add_or_modify(request):
    return post_second_manager_add_or_modify(request, 'wuye')


def post_second_manager_add_or_modify(request, status):
    if request.method == 'POST':  # 当提交表单时
        form = SecondManagerForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            try:
                manager = form.cleaned_data['second_manager_manager']
                user = form.cleaned_data['second_manager_account']
                pw = form.cleaned_data['second_manager_pw']
                name = form.cleaned_data['second_manager_name']
                phone = form.cleaned_data['second_manager_phone']
                company = form.cleaned_data['second_manager_company']
                p = second_manager_add_or_modify(manager, user, pw, name, phone, company, status)
                if p:
                    return JsonResponse(success)
                else:
                    return JsonResponse(fail)
            except Exception, e:
                print e
                return JsonResponse(fail)
        else:
            return JsonResponse(fail)
    else:  # 当正常访问时
        print 'not post'
        return HttpResponseNotFound()


def wuye_search(request):
    try:
        return second_manager_search(request, 'wuye')
    except Exception, e:
        print e
        return JsonResponse(fail)


def mansion_keeper_search(request):
    try:
        return second_manager_search(request, 'mansion')
    except Exception, e:
        print e
        return JsonResponse(fail)


def second_manager_search(request, status):
    company = request.GET.get('second_manager_search_company', "")
    wuye_list = SecondManager.objects.filter(company__icontains=company,
                                             status=status)
    wuye_list = serializers.serialize('json', wuye_list)
    result = {'code': 1,
              'context': wuye_list}
    return JsonResponse(result, safe=False)
#
#
# def post_second_manager_add(request):
#     if request.method == 'POST':  # 当提交表单时
#         form = SecondManagerForm(request.POST)  # form 包含提交的数据
#         if form.is_valid():  # 如果提交的数据合法
#             try:
#                 manager = form.cleaned_data['second_manager_manager']
#                 user = form.cleaned_data['second_manager_user']
#                 pw = form.cleaned_data['second_manager_pw']
#                 name = form.cleaned_data['second_manager_name']
#                 phone = form.cleaned_data['second_manager_phone']
#                 company = form.cleaned_data['second_manager_company']
#                 status = form.cleaned_data['second_manager_status']
#                 p = second_manager_add(manager, user, pw, name, phone, company, status)
#                 return HttpResponse(status=1)
#             except Exception, e:
#                 print e
#                 return HttpResponse(status=0)
#     else:  # 当正常访问时
#         print 'not post'


# 添加一个二级管理员
#
#
# def post_second_manager_modify(request):
#     if request.method == 'POST':  # 当提交表单时
#         form = SecondManagerForm(request.POST)  # form 包含提交的数据
#         if form.is_valid():  # 如果提交的数据合法
#             try:
#                 user = form.cleaned_data['second_manager_user']
#                 pw = form.cleaned_data['second_manager_pw']
#                 name = form.cleaned_data['second_manager_name']
#                 phone = form.cleaned_data['second_manager_phone']
#                 company = form.cleaned_data['second_manager_company']
#                 status = form.cleaned_data['second_manager_status']
#                 p = second_manager_modify(user, pw, name, phone, company, status)
#                 return HttpResponse(status=1)
#             except Exception, e:
#                 print e
#                 return HttpResponse(status=0)
#     else:  # 当正常访问时
#         print 'not post'
#
#
# 修改一个二级管理员


def post_second_manager_delete(request):
    if request.method == 'POST':  # 当提交表单时
        form = SecondManagerUserForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            try:
                user = form.cleaned_data['id']
                p = SecondManager.objects.get(user=user)
                p.delete()
                print 'delete success!'
                return JsonResponse(success)
            except Exception, e:
                print e
                return JsonResponse(fail)
        else:
            return JsonResponse(fail)
    else:  # 当正常访问时
        print 'not post'
        return HttpResponseNotFound()


# 删除一个二级管理员


def post_second_manager_logout(request):
    if request.method == 'POST':  # 当提交表单时
        form = SecondManagerUserForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            try:
                user = form.cleaned_data['id']
                p = second_manager_logout(user)
                if p:
                    return JsonResponse(success)
                else:
                    return JsonResponse(fail)
            except Exception, e:
                print e
                return JsonResponse(fail)
    else:  # 当正常访问时
        print 'not post'
        return HttpResponseNotFound()


def post_second_manager_active(request):
    if request.method == 'POST':  # 当提交表单时
        form = SecondManagerUserForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            try:
                user = form.cleaned_data['id']
                p = second_manager_active(user)
                if p:
                    return JsonResponse(success)
                else:
                    return JsonResponse(fail)
            except Exception, e:
                print e
                return JsonResponse(fail)
    else:  # 当正常访问时
        print 'not post'
        return HttpResponseNotFound()


def post_second_manager_pw(request):
    if request.method == 'POST':
        form = SecondManagerPwdChange(request.POST)
        if form.is_valid():
            try:
                user = form.cleaned_data['second_manager_account']
                oldpw = form.cleaned_data['second_manager_oldpw']
                newpw = form.cleaned_data['second_manager_newpw']
                p = second_manager_pw(user, oldpw, newpw)
                if p:
                    print 'password modify success!'
                    return JsonResponse(success)
                else:
                    print 'password modify fail!'
                    return JsonResponse(fail)
            except Exception, e:
                print e
                return JsonResponse(fail)
        else:
            return JsonResponse(fail)
    else:
        print 'not post'
        return HttpResponseNotFound()


def upload_image(request):
    if request.method == 'POST':
        try:
            image = request.FILES['imageDate']
            folder = time.strftime('%Y%m')
            if not os.path.exists(settings.MEDIA_ROOT + "upload/" + folder):
                os.mkdir(settings.MEDIA_ROOT + "upload/" + folder)
            file_name = time.strftime('%Y%m%d%H%M%S')
            file_ext = image.name.split('.')[-1]
            file_addr = settings.MEDIA_ROOT+"upload/" + folder + "/" + file_name + "." + file_ext
            destination = open(file_addr, 'wb+')
            for chunk in image.chunks():
                destination.write(chunk)
            destination.close()
            result = {
                'files': [{
                    'url': "/media/upload/" + folder + "/" + file_name + "." + file_ext,
                    'thumbnailUrl': "/media/upload/" + folder + "/" + file_name + "." + file_ext,
                    'name': file_name+'.'+file_ext,
                    'size': image.size
                }]
            }
            return JsonResponse(result)
        except Exception, e:
            print "image upload error:"
            print e
            return HttpResponse(status=500)
    else:
        fb = ImageForm()
    return render(request, "home.html", {"r": fb})


def post_roominfo_logout(request):
    if request.method == 'POST':  # 当提交表单时
        form = RoomShortForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            try:
                roomNumber = form.cleaned_data['roomNumber']
                p = roominfo_logout(roomNumber)
                if p:
                    print 'logout success!'
                    return JsonResponse(success)
                else:
                    print 'logout fail'
                    return JsonResponse(fail)
            except Exception, e:
                print "roominfo logout error:"
                print e
                return JsonResponse(fail)
    else:  # 当正常访问时
        print 'not post'
        return HttpResponseNotFound()


def post_roominfo_active(request):
    if request.method == 'POST':  # 当提交表单时
        form = RoomShortForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            try:
                roomNumber = form.cleaned_data['room_roomNumber']
                p = roominfo_active(roomNumber)
                if p:
                    print 'active success!'
                    return JsonResponse(success)
                else:
                    print 'active fail!'
                    return JsonResponse(fail)
            except Exception, e:
                print 'active error:'
                print e
                return JsonResponse(fail)
    else:  # 当正常访问时
        print 'not post'
        return HttpResponseNotFound


def post_roominfo_save(request):
    p, num = post_roominfo_add_or_modify(request)
    if p:
        return JsonResponse(success)
    else:
        return JsonResponse(fail)


def post_roominfo_submit(request):
    p, num = post_roominfo_add_or_modify(request)
    if p:
        try:
            room = RoomInfo.objects.get(roomNumber=num)
            room.achieve = True
            return JsonResponse(success)
        except Exception, e:
            print "post_roominfo_submit error:"
            print e
            return JsonResponse(fail)
    else:
        return JsonResponse(fail)


def post_roominfo_add_or_modify(request):
    if request.method == 'POST':
        try:
            # todo 需要修改
            manager = 'u1'
            roominfo_default = {}
            url_list = []
            for key in request.POST:
                value = request.POST.get(key)
                roominfo_default[str(key)] = value
            url_list = str(roominfo_default['imgUrl'])
            url_list = url_list.split('^_^')
            if '' in url_list:
                url_list.remove('')
            roominfo_default.pop('imgUrl')
            if 'roomNumber' not in roominfo_default:
                roomNumber = get_roomNumber()
                roominfo_default['roomNumber'] = roomNumber
            else:
                roomNumber = roominfo_default['roomNumber']
            roominfo_default['contactPerson'] = manager
            add_or_modify_result = roominfo_add_or_modify(roominfo_default)
            if add_or_modify_result:
                for i in url_list:
                    room_picture_add(roomNumber, i)
            return True, roomNumber
        except Exception, e:
            print "post_roominfo_add_or_modify error:"
            print e
            return False, None
    else:
        return False, None
#
#
# def post_room_save(request):
#     if request.method == 'POST':  # 当提交表单时
#         form = RoomForm(request.POST)  # form 包含提交的数据
#         if form.is_valid():  # 如果提交的数据合法
#             try:
#                 roomNumber = form.cleaned_data['room_roomNumber']
#                 # 房屋信息
#                 room_longitude = form.cleaned_data['room_longitude']
#                 room_latitude = form.cleaned_data['room_latitude']
#                 room_community = form.cleaned_data['room_community']
#                 room_shi = form.cleaned_data['room_shi']
#                 room_ting = form.cleaned_data['room_ting']
#                 room_wei = form.cleaned_data['room_wei']
#                 room_rent = form.cleaned_data['room_rent']
#                 room_area = form.cleaned_data['room_area']
#                 room_direction = form.cleaned_data['room_direction']
#                 room_DateToLive = form.cleaned_data['room_DateToLive']
#                 room_lookAble = form.cleaned_data['room_lookAble']
#                 room_contactPerson = form.cleaned_data['room_contactPerson']
#                 room_environment = form.cleaned_data['room_environment']
#                 # 出租信息
#                 rentDate = form.cleaned_data['rentDate']
#                 # 房屋图片
#                 picture = form.cleaned_data['picture']
#                 # 房屋配置
#                 level = form.cleaned_data['level']
#                 elevator = form.cleaned_data['elevator']
#                 canZhuo = form.cleaned_data['canZhuo']
#                 shaFa = form.cleaned_data['shaFa']
#                 shuZhuo = form.cleaned_data['shuZhuo']
#                 yiZi = form.cleaned_data['yiZi']
#                 yiGui = form.cleaned_data['yiGui']
#                 chuang = form.cleaned_data['chuang']
#                 kongTiao = form.cleaned_data['kongTiao']
#                 xiYiJi = form.cleaned_data['xiYiJi']
#                 reShuiQi = form.cleaned_data['reShuiQi']
#                 bingXiang = form.cleaned_data['bingXiang']
#                 dianShiJi = form.cleaned_data['dianShiJi']
#                 xiYouYanJi = form.cleaned_data['xiYouYanJi']
#                 ranQiZao = form.cleaned_data['ranQiZao']
#                 # 房屋描述
#                 roomType = form.cleaned_data['roomType']
#                 decoration = form.cleaned_data['decoration']
#                 configuration = form.cleaned_data['configuration']
#                 cook = form.cleaned_data['cook']
#                 light = form.cleaned_data['light']
#                 wind = form.cleaned_data['wind']
#                 sound = form.cleaned_data['sound']
#                 requirement = form.cleaned_data['requirement']
#                 suitable = form.cleaned_data['suitable']
#                 p = room_save(roomNumber, room_longitude, room_latitude, room_community, room_shi, \
#                               room_ting, room_wei, room_rent, room_area, room_direction, room_DateToLive, \
#                               room_lookAble, room_contactPerson, room_environment, rentDate, picture, \
#                               level, elevator, canZhuo, shaFa, shuZhuo, yiZi, yiGui, chuang, kongTiao, xiYiJi, reShuiQi, \
#                               bingXiang, dianShiJi, xiYouYanJi, ranQiZao, roomType, decoration, configuration, cook, \
#                               light, wind, sound, requirement, suitable)
#                 return HttpResponse(status=1)
#             except Exception, e:
#                 print e
#                 return HttpResponse(status=0)
#     else:  # 当正常访问时
#         print 'not post'
#
#
# def post_room_sub(request):
#     if request.method == 'POST':  # 当提交表单时
#         form = RoomForm(request.POST)  # form 包含提交的数据
#         if form.is_valid():  # 如果提交的数据合法
#             try:
#                 roomNumber = form.cleaned_data['room_roomNumber']
#                 # 房屋信息
#                 room_longitude = form.cleaned_data['room_longitude']
#                 room_latitude = form.cleaned_data['room_latitude']
#                 room_community = form.cleaned_data['room_community']
#                 room_shi = form.cleaned_data['room_shi']
#                 room_ting = form.cleaned_data['room_ting']
#                 room_wei = form.cleaned_data['room_wei']
#                 room_rent = form.cleaned_data['room_rent']
#                 room_area = form.cleaned_data['room_area']
#                 room_direction = form.cleaned_data['room_direction']
#                 room_DateToLive = form.cleaned_data['room_DateToLive']
#                 room_lookAble = form.cleaned_data['room_lookAble']
#                 room_contactPerson = form.cleaned_data['room_contactPerson']
#                 room_environment = form.cleaned_data['room_environment']
#                 # 出租信息
#                 rentDate = form.cleaned_data['rentDate']
#                 # 房屋图片
#                 picture = form.cleaned_data['picture']
#                 # 房屋配置
#                 level = form.cleaned_data['level']
#                 elevator = form.cleaned_data['elevator']
#                 canZhuo = form.cleaned_data['canZhuo']
#                 shaFa = form.cleaned_data['shaFa']
#                 shuZhuo = form.cleaned_data['shuZhuo']
#                 yiZi = form.cleaned_data['yiZi']
#                 yiGui = form.cleaned_data['yiGui']
#                 chuang = form.cleaned_data['chuang']
#                 kongTiao = form.cleaned_data['kongTiao']
#                 xiYiJi = form.cleaned_data['xiYiJi']
#                 reShuiQi = form.cleaned_data['reShuiQi']
#                 bingXiang = form.cleaned_data['bingXiang']
#                 dianShiJi = form.cleaned_data['dianShiJi']
#                 xiYouYanJi = form.cleaned_data['xiYouYanJi']
#                 ranQiZao = form.cleaned_data['ranQiZao']
#                 # 房屋描述
#                 roomType = form.cleaned_data['roomType']
#                 decoration = form.cleaned_data['decoration']
#                 configuration = form.cleaned_data['configuration']
#                 cook = form.cleaned_data['cook']
#                 light = form.cleaned_data['light']
#                 wind = form.cleaned_data['wind']
#                 sound = form.cleaned_data['sound']
#                 requirement = form.cleaned_data['requirement']
#                 suitable = form.cleaned_data['suitable']
#                 p = room_sub(roomNumber, room_longitude, room_latitude, room_community, room_shi, \
#                              room_ting, room_wei, room_rent, room_area, room_direction, room_DateToLive, \
#                              room_lookAble, room_contactPerson, room_environment, rentDate, picture, \
#                              level, elevator, canZhuo, shaFa, shuZhuo, yiZi, yiGui, chuang, kongTiao, xiYiJi, reShuiQi, \
#                              bingXiang, dianShiJi, xiYouYanJi, ranQiZao, roomType, decoration, configuration, cook, \
#                              light, wind, sound, requirement, suitable)
#                 return HttpResponse(status=1)
#             except Exception, e:
#                 print e
#                 return HttpResponse(status=0)
#     else:  # 当正常访问时
#         print 'not post'
#
#
def post_room_sold(request):
    if request.method == 'POST':  # 当提交表单时
        form = RoomShortForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            try:
                roomNumber = form.cleaned_data['room_roomNumber']
                p = roominfo_sold(roomNumber)
                if p:
                    print 'room has been sold '
                    return JsonResponse(success)
                else:
                    return JsonResponse(fail)
            except Exception, e:
                print 'post roominfo sold error:'
                print e
                return JsonResponse(fail)
    else:  # 当正常访问时
        print 'not post'
        return HttpResponseNotFound()


def post_evaluation_add(request):
    if request.method == 'POST':  # 当提交表单时
        form = RoomEvaluationForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            try:
                roomNumber = form.cleaned_data['roomNumber']
                text = form.cleaned_data['text']
                p = evaluation_add(roomNumber, text)
                if p:
                    print 'evaluation success'
                    return JsonResponse(success)
                else:
                    print 'evaluation fail'
                    return JsonResponse(fail)
            except Exception, e:
                print 'evaluation error:'
                print e
                return JsonResponse(fail)
    else:  # 当正常访问时
        print 'not post'
        return HttpResponseNotFound()


def post_evaluation_pass(request):
    if request.method == 'POST':
        form = RoomEvaluationForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            try:
                e_id = form.cleaned_data['id']
                p = evaluation_pass(e_id)
                if p:
                    print 'evaluation pass success'
                    return JsonResponse(success)
                else:
                    print 'evaluation pass fail'
                    return JsonResponse(fail)
            except Exception, e:
                print 'evaluation pass error:'
                print e
                return JsonResponse(fail)
    else:
        print 'not post'
        return HttpResponseNotFound()


def post_evaluation_no_pass(request):
    if request.method == 'POST':
        form = RoomEvaluationForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            try:
                e_id = form.cleaned_data['id']
                p = evaluation_no_pass(e_id)
                if p:
                    print 'evaluation no pass success'
                    return JsonResponse(success)
                else:
                    print 'evaluation no pass fail'
                    return JsonResponse(fail)
            except Exception, e:
                print 'evaluation no pass error:'
                print e
                return JsonResponse(fail)
    else:
        print 'not post'
        return HttpResponseNotFound()


def post_evaluation_delete(request):
    if request.method == 'POST':  # 当提交表单时
        form = RoomEvaluationForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            try:
                e_id = form.cleaned_data['id']
                p = evaluation_delete(e_id)
                if p:
                    print 'evaluation success'
                    return JsonResponse(success)
                else:
                    print 'evaluation fail'
                    return JsonResponse(fail)
            except Exception, e:
                print 'evaluation error:'
                print e
                return JsonResponse(fail)
    else:  # 当正常访问时
        print 'not post'
        return HttpResponseNotFound()


def post_evaluation_search(request):
    try:
        page = int(request.GET.get('p', 1))
        e = RoomEvaluation.objects.order_by('createTime')[page*10-10:page*10]
        count = RoomEvaluation.objects.count()
        e = serializers.serialize('json', e)
        result = {'code': 1,
                  'count': count,
                  'context': e}
        return JsonResponse(result, safe=False)
    except Exception, e:
        print 'post evaluation search error:'
        print e
        return JsonResponse(fail)


# 增加一条小区信息
def post_community_add(request):
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            manager = form.cleaned_data['xiaoqu_add_manager']
            name = form.cleaned_data['xiaoqu_add_name']
            lng = form.cleaned_data['xiaoqu_add_lng']
            lat = form.cleaned_data['xiaoqu_add_lat']
            area = form.cleaned_data['xiaoqu_add_area']
            district = form.cleaned_data['xiaoqu_add_district']
            business = form.cleaned_data['xiaoqu_add_business']
            keyword = form.cleaned_data['xiaoqu_add_keyword']
            type_ = form.cleaned_data['xiaoqu_add_type']
            year = form.cleaned_data['xiaoqu_add_year']
            level = form.cleaned_data['xiaoqu_add_level']
            facility = form.cleaned_data['xiaoqu_add_facility']
            green = form.cleaned_data['xiaoqu_add_green']
            security = form.cleaned_data['xiaoqu_add_security']
            p = community_add_or_modify(name, manager, lng, lat, area, district, business,
                                        keyword, type_, year, level, facility, green, security)
            if p:
                return JsonResponse(success)
            else:
                return JsonResponse(fail)
        else:
            return JsonResponse(fail)
    else:
        return HttpResponseNotFound()


# 小区查询，返回一个jason 列表
def post_community_search(request):
    try:
        kw = request.GET.get('xiaoqu_search_name', '')
        c_list = get_community_list(kw)
        c_list = serializers.serialize('json', c_list)
        result = {'code': 1,
                  'context': c_list}
        return JsonResponse(result, safe=False)
    except Exception, e:
        print e
        return JsonResponse(fail)


# 小区删除
def post_community_delete(request):
    if request.method == "POST":
        form = CommunityDeleteForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["id"]
            p = community_delete(name)
            if p:
                return JsonResponse(success)
            else:
                return JsonResponse(fail)
        else:
            return JsonResponse(fail)
    else:
        return HttpResponseNotFound()
