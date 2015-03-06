# -*- coding: utf-8 -*-

class BankDataValidator(object):

    def __init__(self,txaCons):
        self.txaCons = txaCons

    def checkDataFormat(self,_Dialog):
        _datafile = _Dialog.fileName
        self.txaCons.append('\''+_datafile+'\' 파일을 분석합니다.')

        try:
            _file = open(_datafile,encoding='cp949')
            _file.readline()
            _fileEnc = 'cp949'
        except UnicodeDecodeError:
            try:
                _file.close()
                _file = open(_datafile,encoding='utf-8')
                _file.readline()
                _fileEnc = 'utf-8'
            except UnicodeDecodeError:
                self.txaCons.append('텍스트 파일이 아닙니다. 암호화 되어 있거나 엑셀파일 인지 확인 하세요.')
                return
        _file.close()

        _Dialog.fileEnc = _fileEnc
        lstData = []
        headerColumnNum = len(_Dialog._header.split('\t'))
        fileLineCnt = 1
        for _line in open(_datafile,encoding=_fileEnc):
            lstData.append(_line)
            if len(_line.split('\t')) == 1:
                self.txaCons.append(str(fileLineCnt)+'행이 탭(TAB)으로 분리되어 있지 않습니다.')
                self.txaCons.append(_line.replace('\t',','))
                return
            if headerColumnNum != len(_line.split('\t')):
                self.txaCons.append(str(fileLineCnt)+'행의 컬럼개수('+str(len(_line.split('\t'))) +
                                    ')가 정의된 헤더 컬럼개수('+str(headerColumnNum)+')와 일치하지 않습니다.')
                self.txaCons.append(_line.replace('\t',','))
                return
            fileLineCnt += 1
        return lstData

if __name__ == '__main__':
    print('Bank Data Validator')