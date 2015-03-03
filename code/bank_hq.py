# -*- coding: utf-8 -*-

import sys
from PySide import QtCore, QtGui
from PySide.QtGui import QRadioButton
from code.bankdata_validator import BankDataValidator
from code.header_info import HeaderInfo

class Dialog(QtGui.QDialog):
    def __init__(self):
        super(Dialog, self).__init__()

        self.dh = HeaderInfo()
        self.fv = BankDataValidator()

        self.createMenu()
        self.createDataTypeGroupBox()
        self.createFindFileBox()
        self.createGenConsole()
        self.createBtnBox()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.dtgBox)
        mainLayout.addWidget(self.ffBox)
        mainLayout.addWidget(self.genConsole)
        mainLayout.addWidget(self.btgBox)
        self.setLayout(mainLayout)
        self.setFixedHeight(self.sizeHint().height())
        self.setFixedWidth(self.sizeHint().width())

        self.setWindowTitle("검사자료 생성")

    def createMenu(self):
        self.menuBar = QtGui.QMenuBar()

    def createDataTypeGroupBox(self):
        self.dtgBox = QtGui.QGroupBox(u'데이터 구분')
        lOut = QtGui.QHBoxLayout()
        self.dGrp = QtGui.QButtonGroup()
        r1 = QRadioButton(u'가계-계좌별');lOut.addWidget(r1);self.dGrp.addButton(r1)
        r2 = QRadioButton(u'가계-차주별');lOut.addWidget(r2);self.dGrp.addButton(r2)
        r3 = QRadioButton(u'가계-상환');lOut.addWidget(r3);self.dGrp.addButton(r3)
        r4 = QRadioButton(u'기업-계좌별');lOut.addWidget(r4);self.dGrp.addButton(r4)
        r5 = QRadioButton(u'기업-차주별');lOut.addWidget(r5);self.dGrp.addButton(r5)
        self.dtgBox.setLayout(lOut)

    def createFindFileBox(self):
        self.ffBox = QtGui.QGroupBox(u'파일 찾기')
        lOut = QtGui.QFormLayout()
        self.txaFileLoc = QtGui.QLineEdit()
        self.txaFileLoc.setFixedWidth(500);self.txaFileLoc.setEnabled(False)
        self.btnFindFile = QtGui.QPushButton(u'열기')
        self.btnFindFile.clicked.connect(self.openFileDialog)
        lOut.addRow(self.txaFileLoc, self.btnFindFile)
        self.ffBox.setLayout(lOut)

    def createGenConsole(self):
        self.genConsole = QtGui.QTextEdit()
        self.genConsole.setFixedHeight(600)

    def createBtnBox(self):
        self.btgBox = QtGui.QGroupBox()
        self.btgBox.setFlat(True)
        lOut = QtGui.QHBoxLayout()
        lOut.setAlignment(QtCore.Qt.AlignRight)
        self.btnGenFile = QtGui.QPushButton(u'실행');self.btnGenFile.setEnabled(False)
        self.btnExit = QtGui.QPushButton(u'종료');self.btnExit.clicked.connect(QtCore.QCoreApplication.instance().quit)
        lOut.addWidget(self.btnGenFile)
        lOut.addWidget(self.btnExit)
        self.btgBox.setLayout(lOut)

    def openFileDialog(self):
        _buttonNum = self.getDataTypeNum();
        if _buttonNum == -1:
            errBox = QtGui.QMessageBox();errBox.setWindowTitle(u'경고')
            errBox.setText(u'데이터 구분을 선택하셔야 합니다.')
            errBox.exec_()
            return
        print(self.dh.getDataType(_buttonNum))
        fileName, _ = QtGui.QFileDialog.getOpenFileName(self, "검사자료 파일", QtCore.QDir.currentPath(), "Text files(*.txt)")
        self.lstData = self.fv.checkDataFormat(fileName)
        self.txaFileLoc.setText(fileName)
        self.btnGenFile.setEnabled(True)

    def getDataTypeNum(self):
        dTButtons = self.dGrp.buttons()
        for i in range(len(dTButtons)):
            _button = dTButtons[i]
            if _button.isChecked():
                return i
        return -1


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())
