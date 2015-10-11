# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.


class RoomInfo(models.Model):
    roomNumber = models.CharField(max_length=10, primary_key=True) # 新加的
    price = models.IntegerField()
    contactPerson = models.CharField(max_length=30)
    addr_xiaoqu = models.CharField(max_length=30)
    addr_building = models.CharField(max_length=30)
    addr_unit = models.CharField(max_length=30)
    addr_floor = models.CharField(max_length=30)
    addr_room = models.CharField(max_length=30)
    payway = models.CharField(max_length=30)
    type_room = models.CharField(max_length=30)
    type_livingroom = models.CharField(max_length=30)
    type_toilet = models.CharField(max_length=30)
    stay_intime = models.DateField()
    see = models.CharField(max_length=30, default='off')
    floor_level = models.CharField(max_length=30)
    total_floor = models.CharField(max_length=30)
    elevator = models.CharField(max_length=30, default='off')
    canzhuo = models.CharField(max_length=30, default='off')
    sofa = models.CharField(max_length=30, default='off')
    desk = models.CharField(max_length=30, default='off')
    chair = models.CharField(max_length=30, default='off')
    closet = models.CharField(max_length=30, default='off')
    bed = models.CharField(max_length=30, default='off')
    aircon = models.CharField(max_length=30, default='off')
    washer = models.CharField(max_length=30, default='off')
    waterheater = models.CharField(max_length=30, default='off')
    refregister = models.CharField(max_length=30, default='off')
    tv = models.CharField(max_length=30, default='off')
    cookerhood = models.CharField(max_length=30, default='off')
    gascooker = models.CharField(max_length=30, default='off')
    original_house_type = models.CharField(max_length=200)
    decorate_level = models.CharField(max_length=200)
    config_level = models.CharField(max_length=200)
    can_cook = models.CharField(max_length=200)
    lighting = models.CharField(max_length=200)
    ventilate = models.CharField(max_length=200)
    noise = models.CharField(max_length=200)
    landlord_req = models.CharField(max_length=200)
    fit_people = models.CharField(max_length=200)
    # imgUrl = models.CharField(max_length=30)
    sold = models.BooleanField(default=False)
    exist = models.BooleanField(default=False)
    achieve = models.BooleanField(default=False)

    def __unicode__(self):
        return self.roomNumber


class Environment(models.Model):
    # 小区环境
    name = models.CharField(max_length=30, primary_key=True)
    shangQuan = models.CharField(max_length=100)
    shuXing = models.CharField(max_length=100)
    nianXian = models.CharField(max_length=100)
    guiMo = models.CharField(max_length=100)
    anBao = models.CharField(max_length=100)


class Community(models.Model):
    # 小区信息
    manager = models.CharField(max_length=30)
    name = models.CharField(max_length=30, primary_key=True)
    item = models.CharField(max_length=100)
    lng = models.FloatField()
    lat = models.FloatField()
    area = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    business = models.CharField(max_length=100)
    keyword = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    year = models.CharField(max_length=100)
    level = models.CharField(max_length=100)
    facility = models.CharField(max_length=100)
    green = models.CharField(max_length=100)
    security = models.CharField(max_length=100)


class Room(models.Model):
    # 房屋信息
    roomNumber = models.CharField(max_length=10, primary_key=True)
    longitude = models.FloatField(default=120.200)
    latitude = models.FloatField(default=30.3)
    shi = models.IntegerField()
    ting = models.IntegerField()
    wei = models.IntegerField()
    rent = models.IntegerField()
    rentStyle = models.CharField(max_length=30)
    area = models.IntegerField()
    direction = models.CharField(max_length=10)
    DateToLive = models.DateField()
    lookAble = models.BooleanField()
    contactPerson = models.CharField(max_length=30)
    community = models.CharField(max_length=30)
    environment = models.CharField(max_length=30)
    sold = models.BooleanField(default=False)
    exist = models.BooleanField(default=False)
    achieve = models.BooleanField(default=False)

    def __unicode__(self):
        return self.roomNumber



class RoomRented(models.Model):
    # 房屋出租信息 todo 还有很多信息需要补全
    roomNumber = models.CharField(max_length=10, primary_key=True)
    rentDate = models.DateField()


class RoomPicture(models.Model):
    # 房屋照片
    roomNumber = models.ForeignKey(Room)
    picture = models.CharField(max_length=100)


class RoomEvaluation(models.Model):
    # 租客评价
    roomNumber = models.ForeignKey(Room)
    creatTime = models.DateTimeField(auto_now_add=True)
    text = models.TextField()


class RoomConfiguration(models.Model):
    # 房屋配置
    roomNumber = models.OneToOneField(Room, primary_key=True)
    level = models.IntegerField()
    elevator = models.BooleanField()
    canZhuo = models.BooleanField()
    shaFa = models.BooleanField()
    shuZhuo = models.BooleanField()
    yiZi = models.BooleanField()
    yiGui = models.BooleanField()
    chuang = models.BooleanField()
    kongTiao = models.BooleanField()
    xiYiJi = models.BooleanField()
    reShuiQi = models.BooleanField()
    bingXiang = models.BooleanField()
    dianShiJi = models.BooleanField()
    xiYouYanJi = models.BooleanField()
    ranQiZao = models.BooleanField()


class RoomDescription(models.Model):
    # 房屋描述
    roomNumber = models.OneToOneField(Room, primary_key=True)
    roomType = models.CharField(max_length=100)
    decoration = models.CharField(max_length=100)
    configuration = models.CharField(max_length=100)
    cook = models.CharField(max_length=100)
    light = models.CharField(max_length=100)
    wind = models.CharField(max_length=100)
    sound = models.CharField(max_length=100)
    requirement = models.CharField(max_length=100)
    suitable = models.CharField(max_length=100)


class Manager(models.Model):
    # 一级管理员
    user = models.CharField(max_length=30, primary_key=True)
    pw = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=11)
    status = models.CharField(max_length=30)
    district = models.CharField(max_length=30)
    exist = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class SecondManager(models.Model):

    # 二级管理员
    manager = models.ForeignKey(Manager)
    user = models.CharField(max_length=30, primary_key=True)
    pw = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=11)
    company = models.CharField(max_length=30)
    status = models.CharField(max_length=30)
    exist = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


# class Uploader(models.Model):
#     # 上传者
#     user = models.CharField(max_length=30, primary_key=True)
#     pw = models.CharField(max_length=30)
#     name = models.CharField(max_length=30)
#     company = models.CharField(max_length=30)
#     exist = models.BooleanField(default=True)
#
#     def __unicode__(self):
#         return self.name
#
#
# class Butler(models.Model):
#     # 管家
#     uploader = models.ForeignKey(Uploader)
#     name = models.CharField(max_length=30)
#     phone = models.CharField(max_length=11)
#     company = models.CharField(max_length=30)
#
#     def __unicode__(self):
#         return self.name
