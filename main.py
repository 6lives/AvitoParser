from kivy.app import App
import os
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.clock import Clock

from threading import Thread
import requests, random, json, os, time, datetime, telebot
from bs4 import BeautifulSoup

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from kivy.config import Config

Config.set("graphics","resizable","0")
Config.set("graphics","width","800")
Config.set("graphics","height","600")



class AvitoApp(App):
    def build(self):
        check = os.path.isfile('config.txt')
        if check:
            with open('config.txt', 'r') as file:
                x = file.read().split(' ')
            self.url = TextInput(hint_text = 'Ссылка на авито(Обязательно)*\nЗайти на авито, выставить нужные фильтры, скопировать сюда ссылку',text = x[0] ,multiline = True, size_hint = [1,.2])
            self.userid = TextInput(hint_text = 'UserId телеграм (Обязательно)*\n@getmyid_bot чтобы узнать свой айди\n@avito_parser123_bot запустить чтобы приходили объявления',text = x[1] ,multiline = False, size_hint = [1,.2])
        else:
            self.url = TextInput(hint_text = 'Ссылка на авито(Обязательно)*\nЗайти на авито, выставить нужные фильтры, скопировать сюда ссылку',multiline = True, size_hint = [1,.2])
            self.userid = TextInput(hint_text = 'UserId телеграм (Обязательно)*\n@getmyid_bot чтобы узнать свой айди\n@avito_parser123_bot запустить чтобы приходили объявления' ,multiline = True, size_hint = [1,.2])

        self.title = 'Avito Parser'
        self.icon = 'logo.ico'
        root = BoxLayout(orientation = "horizontal", padding = 5, spacing = 5)

        self.right = BoxLayout(orientation="vertical")
        self.console = TextInput(readonly = True, hint_text = 'console for some log messages')
        self.right.add_widget(self.console)

        self.left = BoxLayout(orientation='vertical')
        url_lable = Label(text = 'Поле для ссылки: ',size_hint = [1,.05])
        userid_lable = Label(text = 'Поле для айди телеграма: ',size_hint = [1,.05])
        keyword_lable = Label(text = 'Поле ключевого слова для поиска:',size_hint = [1,.05])
        self.keyword = TextInput(hint_text = 'Ключевое слово' ,multiline = False, size_hint = [1,.2])
        self.startbutton = Button(text = 'START',size_hint = [1,.2])

        leftGrid = GridLayout(cols = 2, size_hint = [1,.2])
        minprice_lable = Label(text = 'Мин цена:')
        maxprice_lable = Label(text = 'Макс цена:')
        self.minprice_input = TextInput(text = '0' ,multiline = False)
        self.maxprice_input = TextInput(text = '1000000',multiline = False)
        self.notification = Switch(active = True)
        notification_label = Label(text = 'Звук уведомлений')
        self.startbutton.bind(on_press = self.th_start)

        leftGrid.add_widget(minprice_lable)
        leftGrid.add_widget(self.minprice_input)
        leftGrid.add_widget(maxprice_lable)
        leftGrid.add_widget(self.maxprice_input)
        leftGrid.add_widget(notification_label)
        leftGrid.add_widget(self.notification)

        self.left.add_widget(url_lable)
        self.left.add_widget(self.url)
        self.left.add_widget(userid_lable)
        self.left.add_widget(self.userid)
        self.left.add_widget(keyword_lable)
        self.left.add_widget(self.keyword)
        self.left.add_widget(leftGrid)
        self.left.add_widget(self.startbutton)

        root.add_widget(self.left)
        root.add_widget(self.right)
        #Clock.schedule_interval(self.update, 0.5)
        return root

    def th_start(self, args):
        if self.url.text and self.userid.text:
            with open('config.txt', 'w') as file:
                file.write('{} {}'.format(self.url.text, self.userid.text))
        self.x = Thread(target=self.parse, args=(self.url.text, self.userid.text, self.minprice_input.text, self.maxprice_input.text, self.notification.active,self.keyword.text),daemon=True)
        self.x.start()


    def parse(self, Url,Userid, Min_price, Max_price, Notification, INcontent=''):
        self.console.text += '\n[INFO] Процесс парсинга запущен...\n'

        if not '?' in Url:
            Url += '?s=104'
        if not 's=104' in Url:
            Url += '&s=104'

        token = '2044100299:AAEh3e6UcK1vWenHoDKmUZK8vV5_E_cUkEw'
        bot = telebot.TeleBot(token)
        headers = {
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            '(KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'
        }
        start_time = datetime.datetime.now()
        all_data = {}

        check = os.path.isfile('db.json')
        if not check:
            with open('db.json', 'a', encoding='utf-8') as file:
                json.dump({}, file, indent=4, ensure_ascii=False)
                self.console.text += '\n JSON создан!\n'

        print(Url)

        while True:
            if len(self.console.text) > 750:
                self.console.text = ''

            if not Min_price or not Max_price:
                self.console.text += '\n[ERROR] Обязательно укажите минимальную и максимальную цены!\n'
                break


            with open('db.json', 'r',encoding='utf-8') as file:
                database = json.load(file)

            try:
                req = requests.get(Url, headers = headers)
            except Exception:
                finish_time = datetime.datetime.now()
                result_time = finish_time - start_time
                self.console.text += f'\n[ERROR] Проверьте корректность ссылки!\n'

            soup = BeautifulSoup(req.text, 'lxml')

            try:
                data = soup.find(class_='items-items-kAJAg').contents
            except Exception:
                finish_time = datetime.datetime.now()
                result_time = finish_time - start_time
                self.console.text += f'\n[ERROR] Проверьте корректность ссылки!\n'

            self.left.remove_widget(self.startbutton)
            for i in data[3::-1]:
                id = i.get('data-item-id')
                if id and id not in database.keys():
                    link = i.find(class_='iva-item-titleStep-_CxvN').next.get('href')
                    description = i.find(class_='iva-item-titleStep-_CxvN').next.get('title')
                    full_description = i.find(class_='iva-item-text-_s_vh iva-item-description-S2pXQ text-text-LurtD text-size-s-BxGpL').text
                    if INcontent.lower() in description.lower() or INcontent.lower() in full_description.lower():
                        price = i.find(class_='price-price-BQkOZ').find_all('meta')[1].get('content')
                        if int(Max_price) >= int(price) >= int(Min_price):
                            print(price)

                            if Notification:
                                bot.send_message(int(Userid), f'{price}руб \n\n{description} \n\n https://www.avito.ru{link}',disable_web_page_preview=True)
                            else:
                                bot.send_message(int(Userid), f'{price}руб \n\n{description} \n\n https://www.avito.ru{link}',disable_web_page_preview=True, disable_notification=True)

                            all_data[id] = {'link':'https://www.avito.ru'+link, 'description':description, 'price':price}

                            database.update(all_data)
                            if len(database.keys()) > 6:
                                for i in list(database.keys())[-4::-1]:
                                    database.pop(i)
                                    print('База обновлена!')

                            with open('db.json', 'w', encoding='utf-8') as file:
                                json.dump(database, file, indent=4, ensure_ascii=False)
                                all_data = {}
                                self.console.text += '\n[INFO] Поступили новые данные\n'
                                print('-'*10)
            time.sleep(random.randrange(3, 5))


if __name__ == '__main__':
    AvitoApp().run()
