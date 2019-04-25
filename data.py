#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser as cp

class Data():
    def __init__(self):
        self.Log_Directory = ''
        self.cmd_list = []

    def readini(self):
        try:
            config = cp.ConfigParser()
            config.read('setting/setting.ini')

            # INITIAL_SETTING
            self.Log_Directory = config.get('INITIAL_SETTING', 'LOG_DIRECTORY')



            cmd_items = config.items('CMD')
            for value in dict(cmd_items).values():
                self.cmd_list.append(value)
        except:
            print('read .ini fail')

        
DATA = Data()


# if __name__ == '__main__':
#     d = Data()
#     d.readini()