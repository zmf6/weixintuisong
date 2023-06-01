import random
from time import localtime
from requests import get, post
from datetime import datetime, date
from zhdate import ZhDate
import sys
import os
import json


def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)


def get_access_token(app_id, app_secret):
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    return access_token


def get_weather(region, key):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    region_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}".format(region, key)
    response = get(region_url, headers=headers).json()
    if response["code"] == "404":
        print("推送消息失败，请检查地区名是否有误！")
        os.system("pause")
        sys.exit(1)
    elif response["code"] == "401":
        print("推送消息失败，请检查和风天气key是否正确！")
        os.system("pause")
        sys.exit(1)
    else:
        # 获取地区的location--id
        location_id = response["location"][0]["id"]
    weather_url = "https://devapi.qweather.com/v7/weather/now?location={}&key={}".format(location_id, key)
    response = get(weather_url, headers=headers).json()
    # 天气
    weather = response["now"]["text"]
    # 当前温度
    temp = response["now"]["temp"] + u"\N{DEGREE SIGN}" + "C"
    # 获取每日天气数据
    daily_data = response["daily"]
    # 最高温度
    temp_max = daily_data["tempMax"] + u"\N{DEGREE SIGN}" + "C"
    # 最低温度
    temp_min = daily_data["tempMin"] + u"\N{DEGREE SIGN}" + "C"
    # 风向
    wind_dir = response["now"]["windDir"]
    return weather, temp, temp_max, temp_min, wind_dir


def calculate_love_days(love_date):
    today = date.today()
    love_start_date = datetime.strptime(love_date, "%Y-%m-%d").date()
    love_days = (today - love_start_date).days
    return love_days


def send_message(to_user, access_token, template_id, region_name, weather, temp, temp_max, temp_min, wind_dir,
                 note_ch, note_en, birthday1, birthday2, love_days):
    url = ("https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}"
           .format(access_token))

    template_data = {
        "weather": "和风天气：{}，最高温度{}，最低温度{}".format(weather, temp_max, temp_min),
        "birthday1": "亲爱的{}，祝你生日快乐！".format(birthday1),
        "birthday2": "亲爱的{}，祝你生日快乐！".format(birthday2),
        "love_date": "我们在一起的日子已经{}天啦！".format(love_days),
        "note_ch": note_ch,
        "note_en": note_en
    }

    zh_date = ZhDate(date.today()).to_date_string()
    en_date = week_list[localtime().tm_wday]
    msg = {
        "touser": to_user,
        "template_id": template_id,
        "data": {
            "first": {
                "value": "{}\n\n".format(template_data["note_ch"]),
                "color": get_color()
            },
            "keyword1": {
                "value": "{}".format(region_name),
                "color": get_color()
            },
            "keyword2": {
                "value": "{}".format(template_data["weather"]),
                "color": get_color()
            },
            "keyword3": {
                "value": "{}-{}".format(temp_min, temp_max),
                "color": get_color()
            },
            "keyword4": {
                "value": "{}".format(wind_dir),
                "color": get_color()
            },
            "keyword5": {
                "value": "{}".format(zh_date),
                "color": get_color()
            },
            "remark": {
                "value": "{}\n\n".format(template_data["note_en"]),
                "color": get_color()
            }
        }
    }
    post(url, json=msg)


if __name__ == '__main__':
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    app_id = config["app_id"]
    app_secret = config["app_secret"]
    weather_key = config["weather_key"]
    region_name = config["region"]
    to_user = config["user"]
    template_id = config["template_id"]
    note_ch = config["note_ch"]
    note_en = config["note_en"]
    birthday1 = config["birthday1"]["name"]
    birthday2 = config["birthday2"]["name"]
    love_date = config["love_date"]

    access_token = get_access_token(app_id, app_secret)
    weather, temp, temp_max, temp_min, wind_dir = get_weather(region_name, weather_key)
    love_days = calculate_love_days(love_date)

    send_message(to_user, access_token, template_id, region_name, weather, temp, temp_max, temp_min, wind_dir,
                 note_ch, note_en, birthday1, birthday2, love_days)
