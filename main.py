import requests
import json
import time
import re
from requests.exceptions import ConnectionError

class Asf:
    def __init__(self, ip, port, password):
        self.address = f'{ip}:{port}'
        self.password = password
        self.headers = {'Authentication': self.password}
        self.check_password()
        self.get_bots()

    def check_password(self):
        url = f'http://{self.address}/api/asf'
        try:
            while True:
                req = requests.get(url, headers=self.headers)
                if req.status_code == 200:
                    print('Вы успешно авторизовались')
                    return True
                else:
                    print('Вы ввели неверный пароль, введите пароль еще раз')
                    password = input()
                    self.set_password(password)
        except ConnectionError:
            print('Сервер не был найден, возможно неправильный адрес.')
            exit()

    def set_password(self, password):
        self.password = password
        self.headers = {'Authentication': password}

    def get_bots(self):
        self.bots = {}
        url = f'http://{self.address}/api/bot/asf'

        req = requests.get(url, headers=self.headers)
        data = json.loads(req.text)
        for botName, values in data['Result'].items():
            if values['KeepRunning']:
                self.bots[botName] = values['s_SteamID']
        return self.bots

    def get_badge(self, name:str = ''):
        print('Начал получать значки!')
        try:
            if name:
                if name not in self.bots:
                    print('Бот не был найден!')
                else:
                    url = f'http://{self.address}/api/Web/{name}/https://store.steampowered.com/replay'
                    requests.get(url, headers=self.headers)
                    result = name + ' Recieve Badge' if self.check_badge(name) else ' Error get badge!'
                    print(result)
            else:
                self.result = {}
                for bot in self.bots:
                    url = f'http://{self.address}/api/Web/{bot}/https://store.steampowered.com/replay'
                    requests.get(url, headers=self.headers)
                    check = self.check_badge(bot)
                    self.result[bot] = check
                    if check:
                        print(bot, 'recived badge')
                    else:
                        print(bot, 'not recived badge')
                self.save_file(self.result)
            print('Успешно закончил получение значков')
        except ConnectionError:
            print('Проблемы с интернетом или сервер ASF упал.')

    def check_badge(self, name:str = '', badge='64'):
        if name:
            if name not in self.bots:
                print('Бот не был найден!')
                return False
            url = f'https://steamcommunity.com/profiles/{self.bots[name]}/badges/{badge}'
            req = requests.get(url)
            print('Recived' if req.url == url else 'Not Recived')
            return True if req.url == url else False
        else:
            self.result = {}
            for name, id in self.bots.items():
                url = f'https://steamcommunity.com/profiles/{id}/badges/{badge}'
                req = requests.get(url)
                if req.url == url:
                    self.result[name] = True
                else:
                    self.result[name] = False
                print(name, self.result[name])
                time.sleep(.5)
            self.save_file(self.result)
            print(self.result)

    def bots_without_badge(self):
        return [i for i, v in self.result.items() if not v]

    def save_file(self, data):
        with open('result.txt', 'w', encoding='utf-8', newline='\n') as file:
            print(self.address, file=file)
            for name, result in data.items():
                print(name, result, file=file)

def input_ip():
    print('Введите IP')
    ip = input()
    check = re.match(r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$', ip)
    while not check:
        print('Введите корректный IP')
        ip = input()
        check = re.fullmatch(r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$', ip)
    return ip

def input_port():
    print('Введите Port')
    port = input()
    check = re.fullmatch(r'^[\d]{3,5}$', port)
    while not check:
        print('Введите корректный порт')
        port= input()
        check = re.fullmatch(r'^[\d]{3,5}$', port)
    return port

def start():
    ip = input_ip()
    port = input_port()
    print('Введите пароль от ASF')
    password = input()
    asf = Asf(ip, port, password)
    command = input().lower()
    while command not in ['exit', 'close']:
        if command == 'get_bots':
            print('Получил', len(asf.get_bots()), 'ботов.')
        elif command == 'check_badge':
            print("""all - Если вы хотите получить значки на всех аккаунтах
<botname> - Получить значок только на этом аккаунте""")
            name = input()
            if name == 'all' or name == '':
                asf.check_badge()
            else:
                asf.check_badge(name)
        elif command == 'get_badge':
            print("""all - Если вы хотите получить значки на всех аккаунтах
<botname> - Получить значок только на этом аккаунте""")
            name = input()
            if name == 'all' or name == '':
                asf.get_badge()
            else:
                asf.get_badge(name)
        elif command == 'get_bots_not_badges':
            print(asf.bots_without_badge())
        else:
            print('Такой команды нет.')
        command = input().lower()

if __name__ == '__main__':
    start()
