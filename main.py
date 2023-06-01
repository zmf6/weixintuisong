import os
import sys
import json
from datetime import datetime, date
from requests import get, post


def get_color():
    colors = ["#FF5722", "#FF9800", "#FFC107", "#FFEB3B", "#CDDC39", "#8BC34A", "#4CAF50", "#009688", "#00BCD4",
              "#03A9F4", "#2196F3", "#3F51B5", "#673AB7", "#9C27B0", "#E91E63", "#F44336"]
    today = datetime.now().day
    return colors[today % len(colors)]


def get_access_token():
    try:
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": config["app_id"],
            "secret": config["app_secret"]
        }
        response = get(url, params=params).json()
        return response["access_token"]
    except:
        print("获取 access_token 失败")
        os.system("pause")
        sys.exit(1)


def get_weather(region):
    try:
        url = "https://free-api.heweather.net/s6/weather/forecast"
        params = {
            "location": region,
            "key": config["weather_key"]
        }
        response = get(url, params=params).json()
        forecast = response["HeWeather6"][0]["daily_forecast"][0]
        weather = forecast["cond_txt_d"]
        temp_max = forecast["tmp_max"]
        temp_min = forecast["tmp_min"]
        wind_dir = forecast["wind_dir"]
        return weather, temp_max, temp_min, wind_dir
    except:
        print("获取天气信息失败")
        os.system("pause")
        sys.exit(1)


def get_birthday(birthday, year, today):
    birthday = date.fromisoformat(birthday)
    if birthday.month > today.month or (birthday.month == today.month and birthday.day >= today.day):
        year_date = date(year, birthday.month, birthday.day)
    else:
        r_last_birthday = date(year, birthday.month, birthday.day)
        r_next_birthday = date((year + 1), birthday.month, birthday.day)
        if (r_next_birthday - today).days > (today - r_last_birthday).days:
            birthday_month = r_next_birthday.month
            birthday_day = r_next_birthday.day
        else:
            birthday_month = r_last_birthday.month
            birthday_day = r_last_birthday.day
        year_date = date((year + 1), birthday_month, birthday_day)
    days_left = (year_date - today).days
    return days_left


def send_message(user, message):
    template = """
    <div id="main" style="background:{};padding:30px;">
        <h2>{}，祝你好运！</h2>
        <p>{}</p>
        <p>今天是{}，</p>
        <p>天气：{}，最高温度：{}℃，最低温度：{}℃，风向：{}</p>
        <p>{}</p>
    </div>
    """
    color = get_color()
    today = datetime.now().date()
    year = today.year
    month = today.month
    day = today.day
    birthday_data = config[user]
    birthday = birthday_data["birthday"]
    days_left = get_birthday(birthday, year, today)
    weather, temp_max, temp_min, wind_dir = get_weather(config["region"])
    message = message.replace("{{birthday1.name}}", birthday_data["name"]).replace("{{birthday2.name}}",
                                                                                   birthday_data["name"]).replace(
        "{{love_days}}", str((today - datetime.fromisoformat(config["love_date"]).date()).days)).replace(
        "{{max_temp}}", temp_max).replace("{{min_temp}}", temp_min)
    message = template.format(color, user, message, "{}年{}月{}日".format(year, month, day), weather, temp_max, temp_min,
                              wind_dir, days_left)
    access_token = get_access_token()
    url = "https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token=" + access_token
    data = {
        "touser": user,
        "template_id": config["template_id"],
        "data": {
            "thing1": {
                "value": user
            },
            "thing2": {
                "value": message
            }
        }
    }
    headers = {'Content-Type': 'application/json'}
    response = post(url, data=json.dumps(data), headers=headers).json()
    if response["errcode"] == 0:
        print("发送成功")
    else:
        print("发送失败")


def main():
    for user in config["user"]:
        send_message(user, config["template_data"]["weather"])
        send_message(user, config["template_data"]["birthday1"])
        send_message(user, config["template_data"]["birthday2"])
        send_message(user, config["template_data"]["love_date"])
        send_message(user, config["template_data"]["note_ch"])
        send_message(user, config["template_data"]["note_en"])


if __name__ == "__main__":
    with open("config.json", "r") as file:
        config = json.load(file)
    main()
