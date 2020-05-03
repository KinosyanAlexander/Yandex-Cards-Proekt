#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QGraphicsScene
from PyQt5.QtGui import QPixmap, QImage

import requests

 
class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui',self)

        screen_geometry = QApplication.desktop().availableGeometry()
        screen_size = (screen_geometry.width(), screen_geometry.height())

        x, y = (screen_size[0] - self.width()) // 2, (screen_size[1] - self.height()) // 2

        self.setGeometry(x, y, self.width(), self.height())

        self.map_file = "map.png"



        self.zoom = 5
        self.coords=[37.620070, 55.753630]



        self.change_img_view(zoom=self.zoom)

        self.pgup.clicked.connect(lambda: self.scale('up'))
        self.pgdown.clicked.connect(lambda: self.scale('down'))

        self.up.clicked.connect(lambda: self.move('up'))
        self.down.clicked.connect(lambda: self.move('down'))
        self.left.clicked.connect(lambda: self.move('left'))
        self.right.clicked.connect(lambda: self.move('right'))


    def change_img_view(self, **kwargs):
        self.make_map_img(**kwargs)

        self.image = QPixmap.fromImage(QImage(self.map_file))

        self.map = QGraphicsScene()
        self.map.addPixmap(self.image)

        self.map_viewer.setScene(self.map)

    
    def make_map_img(self, coords=[37.620070, 55.753630], type='map', size=[450, 450], zoom=10, scale=2, pt=None, pl=None, lang=None):
        coords = self.coords
        zoom = self.zoom
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
              f'z={items["zoom"]}',
              f'l={items["type"]}',
              f'scale={items["scale"]}']
        
        if pt:
            url.append(f'pt={items["pt"]}')
        if pl:
            url.append(f'pl={items["pl"]}',)

        url = '&'.join(url)
        print(url)
        response = requests.get(url)
        print(response)

        # print(response.content)
        
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        # self.pushButton.clicked.connect(self.run)

    def scale(self, way):
        if way == 'up' and self.zoom < 17:
            self.zoom += 1
            # print(self.zoom)
            self.change_img_view(zoom=self.zoom)
        elif way == 'down' and self.zoom > 0:
           self.zoom -= 1
           # print(s1elf.zoom)
           self.change_img_view(zoom=self.zoom)
    
    def move(self, orientation):
        change = 180 / (2 ** self.zoom)
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





 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())