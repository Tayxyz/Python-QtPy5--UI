#!/usr/bin/python3
# -*- coding: utf-8 -*-


import visa


class Fixture:
    def __init__(self):
        # self.read()
        self.rm = visa.ResourceManager()  # 创建对象

    def check_smd(self, cmd):
        if cmd.endswith('?'):
            # print('query')
            return self.inst.query(cmd)
        else:
            # print('write')
            return self.inst.write(cmd)

    def senddir(self, argv):
        # if 'cmd' not in argv:
        #     return 'no cmd'
        try:
            addr = self.rm.list_resources()[0]
            self.inst = self.rm.open_resource(addr)
            result = self.check_smd(argv)
            return result
        except Exception as e:
            return str(Exception) + str(e)



if __name__ == '__main__':
    print(Fixture().connect_query('READ?'))

