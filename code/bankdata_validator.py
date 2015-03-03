# -*- coding: utf-8 -*-

class BankDataValidator(object):

    def checkDataFormat(self,_datafile):
        lstData = []
        for _line in open(_datafile):
            lstData.append(_line)
        return lstData

if __name__ == '__main__':
    print('Bank Data Validator')