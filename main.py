#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QGraphicsScene
from PyQt5.QtGui import QPixmap, QImage

import requests
import math


class MyGraphicsScene(QGraphicsScene):
    def __init__ (self, parent=None):
        super(MyGraphicsScene, self).__init__()
        self.parent = parent

    def mousePressEvent(self, event):
        super(MyGraphicsScene, self).mousePressEvent(event)

        x, y = event.scenePos().x(), event.scenePos().y()

        # print(x, y)
        zoom = self.parent.zoom[0]

        start_coord = list(self.parent.coords)

        start_coord[0] -= zoom / 2
        start_coord[1] += zoom / 2

        coord_change = zoom / 450
        pos = [0, 0]
        pos[0] = start_coord[0] + coord_change * x
        pos[1] = start_coord[1] - coord_change * y

        
        poswww, adress, post_index = self.parent.get_pos_and_adress(pos)

        if event.button() == 1:
            self.parent.search_label.setText(adress)
            
            
            self.parent.search_obj(change_pos=False, my_pos=pos)
        else:
            self.parent.find_org(pos, adress)





 
class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui',self)

        screen_geometry = QApplication.desktop().availableGeometry()
        screen_size = (screen_geometry.width(), screen_geometry.height())

        x, y = (screen_size[0] - self.width()) // 2, (screen_size[1] - self.height()) // 2

        self.setGeometry(x, y, self.width(), self.height())

        self.map_file = "map.png"

        self.zoom = [0.002, 0.002]
        self.coords=[37.620070, 55.753630]
        self.types = ['map', 'sat', 'sat,skl']
        self.type = 0
        self.pt = None



        self.change_img_view(zoom=self.zoom)

        self.pgup.clicked.connect(lambda: self.scale('up'))
        self.pgdown.clicked.connect(lambda: self.scale('down'))

        self.up.clicked.connect(lambda: self.move('up'))
        self.down.clicked.connect(lambda: self.move('down'))
        self.left.clicked.connect(lambda: self.move('left'))
        self.right.clicked.connect(lambda: self.move('right'))

        self.change_map_type.clicked.connect(lambda: self.change_type())

        self.search_button.clicked.connect(lambda: self.search_obj())

        self.clean_button.clicked.connect(lambda: self.clean_map())

        self.post_index_button.setChecked(False)
        self.post_index = 0
        self.post_index_button.toggled.connect(self.change_post_index)


    def change_img_view(self, **kwargs):
        self.make_map_img(**kwargs)

        self.image = QPixmap.fromImage(QImage(self.map_file))

        self.map = MyGraphicsScene(parent=self)
        self.map.addPixmap(self.image)

        self.map_viewer.setScene(self.map)

    def make_map_img(self, coords=[37.620070, 55.753630], type='map', size=[450, 450], zoom=[0.02, 0.02],  pt=None, pl=None, lang=None):
        coords = self.coords
        zoom = self.zoom
        type = self.types[self.type]
        if self.type != 0:
            self.map_file = 'map.jpg'
        else:
            self.map_file = 'map.png'
        if self.pt:
            pt = self.pt
        kwargs = locals()
        kwargs.pop('self')
        # print(kwargs)
        items = list(map(lambda x: [x, kwargs[x]], kwargs))
        # items = list(filter(lambda x: x[1], items))
        # print(items)
        items = dict(map(lambda x: [x[0], ','.join(list(map(lambda y: str(y), x[1]))) 
                         if x[1].__class__.__name__ == 'list'
                         else str(x[1])], items))

        # def make_url_format_items(**kwargs):
            # for item in **kwargs:
                # if type(item).__name__ == 'list':
                    # if str(item) != 'pt' or 'pl':

        # print(items)
        # api_key = "40d1649f-0493-4b70-98ba-98533de7710b"

        url = [f'https://static-maps.yandex.ru/1.x/?ll={items["coords"]}', 
              f'size={items["size"]}',
              f'spn={items["zoom"]}',
              f'l={items["type"]}']
        
        if pt:
            url.append(f'pt={items["pt"]}')
        if pl:
            url.append(f'pl={items["pl"]}')


        url = '&'.join(url)
        print(url)
        response = requests.get(url)#, proxies={'https': 'socks4://195.9.17.5:39264'})
        print(response)

        # print(response.content)
        
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        # self.pushButton.clicked.connect(self.run)

    def scale(self, way):
        if way == 'down':
            if self.zoom[0] * 2 < 90:
                self.zoom[0] *= 2
                self.zoom[1] *= 2
            else:
                self.zoom = [90, 90]
            # print(self.zoom)
            self.change_img_view(zoom=self.zoom)
        elif way == 'up' and self.zoom[0] > 0.002:
           self.zoom[0] /= 2
           self.zoom[1] /= 2
           # print(s1elf.zoom)
           self.change_img_view(zoom=self.zoom)

    def move(self, orientation):
        change = self.zoom[0]
        if orientation == 'up':
            new_y = self.coords[1] + change
            new_x = self.coords[0]
        elif orientation == 'down':
            new_y = self.coords[1] - change
            new_x = self.coords[0]
        elif orientation == 'right':
            new_x = self.coords[0] + change
            new_y = self.coords[1]
        elif orientation == 'left':
            new_x = self.coords[0] - change
            new_y = self.coords[1]
        
        if new_y < 90 and new_y > -90 and new_x < 180 and new_x > -180:
            self.coords = [new_x, new_y]
            self.change_img_view()

    def change_type(self):
        self.type += 1
        
        try:
            self.types[self.type]
        except IndexError:
            self.type = 0
        finally:
            self.change_img_view()

    def get_pos_and_adress(self, text_zap):
        if text_zap.__class__.__name__ == 'list':
            text_zap = ','.join(list(map(lambda x: str(x), text_zap)))
        # ",+".join(text_zap.split(","))
        url = f'https://geocode-maps.yandex.ru/1.x/?geocode={text_zap}&apikey=40d1649f-0493-4b70-98ba-98533de7710b&format=json'
        print(url)
        try:
            zap = requests.get(url)
            # print('jsondjrbf', zap.json())
            sp = zap.json()["response"]["GeoObjectCollection"]["featureMember"]
            top = sp[0]["GeoObject"]
            pos = top['Point']['pos'].split()
            pos = list(map(lambda x: float(x), pos))
            # print(top)
            
            adress = top['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
            try:
                post_index = top['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
                # post_index = top['metaDataProperty']['AddressDetails']['Country']['AdministrativeArea']['Locality']['Thoroughfare']['Premise']['PostalCode']['PostalCodeNumber']
            except KeyError:
                post_index = None
                print('No post Index')
            return pos, adress, post_index
        except IndexError:
            return None

    def search_obj(self, change_pos=True, my_pos=None):
        pos, adress, post_index = self.get_pos_and_adress(self.search_label.text())
        if pos:
            if self.post_index and post_index:
                adress = f'{adress}, {post_index}'
            self.adress_line.setText(adress)
            if change_pos:
                print('ch pos')
                self.coords = pos
            if my_pos:
                print(my_pos)
                pos = my_pos
            self.pt = f'{pos[0]},{pos[1]},pm2rdl'
            self.change_img_view(pt=self.pt)
        else:
            print('No matches(')
    
    def clean_map(self):
        self.pt = None
        self.adress_line.setText('')
        self.search_label.setText('')
        self.change_img_view()
    
    def change_post_index(self):
        self.post_index += 1
        self.post_index = self.post_index % 2
        pos, adress, post_index = self.get_pos_and_adress(self.search_label.text())
        if self.post_index and post_index:
            adress = f'{adress}, {post_index}'
        self.adress_line.setText(adress)

    def find_org(self, pos, adress):
        try:
            search_api_server = "https://search-maps.yandex.ru/v1/"
            api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
            search_params = {
                "apikey": api_key,
                "lang": "ru_RU",
                "text": adress,
                "ll": ','.join(list(map(lambda x: str(x), pos))),
                "spn": '0.0008,0.0008',
                "rspn": 1,
                "type": "biz"
            }
            response = requests.get(search_api_server, params=search_params)
            print(response.url)
            if not response:
                print("Ошибка выполнения запроса:")
                print(response.url)
                print("Http статус:", response.status_code, "(", response.reason, ")")
                sys.exit(1)
            json_response = response.json()
            organization = json_response["features"][0]
            # org_address = organization["properties"]["CompanyMetaData"]["address"]
            # Получаем координаты ответа.
            info = organization['properties']['CompanyMetaData']
            org_name = info['name']
            adress = info['address']
            print('name', org_name, 'adress', adress)
            self.search_label.setText(adress + ' ' + org_name)
            pos = organization["geometry"]["coordinates"]
            self.search_obj(change_pos=False, my_pos=pos)
        except Exception as e:
            print(e)
        # points = organization["geometry"]["coordinates"]
        # return points


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())