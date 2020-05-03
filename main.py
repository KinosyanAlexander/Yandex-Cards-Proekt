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

        self.make_map_img()

        self.image = QPixmap.fromImage(QImage(self.map_file))

        self.map = QGraphicsScene()
        self.map.addPixmap(self.image)

        self.map_viewer.setScene(self.map)

    
    def make_map_img(self, coords=[37.620070, 55.753630], type='map', size=[450, 450], scale_level=10, scale=2, pt=None, pl=None, lang=None):
        kwargs = locals()
        kwargs.pop('self')
        # print(kwargs)
        items = list(map(lambda x: [x, kwargs[x]], kwargs))
        items = list(filter(lambda x: x[1], items))
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
              f'z={items["scale_level"]}',
              f'l={items["type"]}',
              f'scale={items["scale"]}']
        
        if pt:
            url.append(f'pt={items["pt"]}')
        if pl:
            url.append(f'pl={items["pl"]}',)

        url = '&'.join(url)
        print(url)
        response = requests.get(url)

        # print(response.content)
        
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        # self.pushButton.clicked.connect(self.run)


 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())