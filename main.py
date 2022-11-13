import schedule # таймер для отавки по времени
import requests
import time
import json
from datetime import datetime


def log(text, level):
    daytime = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    TEXT = F"{daytime} | mpei-weather | {level} | {text}"
    print(TEXT)

def logo():
    print("""                         
    __  ___           _    _       __           __  __             
   /  |/  /___  ___  (_)  | |     / /__  ____ _/ /_/ /_  ___  _____
  / /|_/ / __ \/ _ \/ /   | | /| / / _ \/ __ `/ __/ __ \/ _ \/ ___/
 / /  / / /_/ /  __/ /    | |/ |/ /  __/ /_/ / /_/ / / /  __/ /    
/_/  /_/ .___/\___/_/     |__/|__/\___/\__,_/\__/_/ /_/\___/_/     
      /_/""")

def load_config():
    with open('config.json', 'r') as f:
        CONFIG = json.load(f)
    return CONFIG

def load_weather(USER, CONFIG):
    USER_SETTINGS = load_config()["USERS"][USER]
    log(f"Load weather for {USER_SETTINGS['NAME']}...", level='i')
    url = "https://yahoo-weather5.p.rapidapi.com/weather"

    querystring = {"location": USER_SETTINGS['LOCATION'], "format": "json", "u": "c"}
    headers = {
        "X-RapidAPI-Key": CONFIG['SETUP']['WEATHER_KEY'],
        "X-RapidAPI-Host": CONFIG['SETUP']['WEATHER_HOST']
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    a = response.json()['forecasts'][0]
    weather = {
        "day": datetime.fromtimestamp(a['date']).strftime("%D"),
        "low": a['low'],
        "high": a['high'],
        "txt": a['text']
    }
    return weather

def send_sms(USER, weather):
    CONFIG = load_config()
    USER_SETTINGS = CONFIG["USERS"][USER]
    log(f"Send SMS for {USER_SETTINGS['NAME']}", level='i')
    datetime = time.strftime("%d.%m.%Y")
    MEASSAGE_TEXT = F"Привет, {USER_SETTINGS['NAME']}! Сегодня {datetime}.\nПогода на сегодня: {weather['txt']}. \nТемпература от {weather['low']} до {weather['high']} градусов. \n\nСпасибо, что пользуешься нашим сервисом!"
    req = requests.get(f'http://smspilot.ru/api.php?send={MEASSAGE_TEXT}&to={USER_SETTINGS["PHONE"]}&from={CONFIG["SETUP"]["SMS_SENDER"]}&apikey={CONFIG["SETUP"]["SMS_KEY"]}&format=json')
    try:
        error = req.json()['error']
        log(f"Error: {error}", level='e')
    except:
        log(f"SMS sended! to {USER_SETTINGS['NAME']} ", level='i')

def load_timer():
    CONFIG = load_config()
    log(F"Loading timer...", level='!')
    log(F"loaded {len(CONFIG['USERS'])} users...", level='i')
    for USER in CONFIG['USERS']:
        for TIME in CONFIG['USERS'][USER]['TIME']:
            log(f"Added new job for {CONFIG['USERS'][USER]['NAME']}: {TIME}", level='i')
            schedule.every().day.at(TIME).do(main, USER)
    log(f"Total jobs: {len(schedule.get_jobs())}", level='i')
    log(F"Started successfully!", level='i')

def main(USER):
    weather = load_weather(USER, load_config())
    send_sms(USER, weather)

def test_send():
    CONFIG = load_config()
    inn = input("Send sms without timer (now) ? (y/n)  ")
    if inn.lower() == 'y':
        for USER in CONFIG["USERS"]:
            send_sms(USER, load_weather(USER, CONFIG))


if __name__ == '__main__':
    logo()
    test_send()
    load_timer()
    while True:
        schedule.run_pending()
        time.sleep(1)