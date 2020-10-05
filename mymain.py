from PyQt5.QtWidgets import *
from PyQt5 import QtGui,Qt,QtCore
from mainwidget import Ui_mainwidget
import sys
import os
import socket
from utils import *
class mainwidget(QWidget):
    endloginobj=pyqtSignal()
    endmlsdobj=pyqtSignal()
    endpwdobj=pyqtSignal()
    endcwdobj=pyqtSignal()
    endmkdobj=pyqtSignal()
    endupobj=pyqtSignal()
    enddownobj=pyqtSignal()
    def __init__(self,parent=None):
        super(mainwidget, self).__init__(parent)
        self.ui=Ui_mainwidget()
        self.ui.setupUi(self)
        self.controlsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.datasocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.mshow()
        self.ui.login_ptn.clicked.connect(self.login)
        self.ui.tableWidget.cellDoubleClicked.connect(self.process_doubleclick)
        self.ui.ip_edit.setText('192.168.1.10')
        self.ui.acc_edit.setText('onp')
        self.ui.pass_edit.setText('6324')
        self.ui.tableWidget.setShowGrid(False)
        self.ui.up_ptn.clicked.connect(self.up)
        self.ip=''
        self.acc=''
        self.pwd=''
        self.filepos='/'
        self.ui.dir_ptn.clicked.connect(self.MKD)
        self.file=''
        self.ui.down_ptn.clicked.connect(self.down)
        self.localfile=''
        self.remotefile=''
        self.tag=0
        self.working=''
        self.ui.stop_ptn.clicked.connect(self.mstop)
        self.ui.retry_ptn.setVisible(False)
        self.ui.retry_ptn.clicked.connect(self.retry)
        self.info={}

    def mhide(self):
        self.ui.quit_ptn.setVisible(False)
        self.ui.login_ptn.setVisible(False)
        self.ui.acc_edit.setVisible(False)
        self.ui.ip_edit.setVisible(False)
        self.ui.pass_edit.setVisible(False)
        self.ui.acc_label.setVisible(False)
        self.ui.ip_label.setVisible(False)
        self.ui.pass_label.setVisible(False)

        self.ui.tableWidget.setVisible(True)
        self.ui.up_ptn.setVisible(True)
        self.ui.down_ptn.setVisible(True)
        self.ui.progressBar.setVisible(True)
        self.ui.dir_ptn.setVisible(True)
        self.ui.diredit.setVisible(True)
        #self.ui.stop_ptn.setVisible(True)

    def mshow(self):
        self.ui.quit_ptn.setVisible(True)
        self.ui.login_ptn.setVisible(True)
        self.ui.acc_edit.setVisible(True)
        self.ui.ip_edit.setVisible(True)
        self.ui.pass_edit.setVisible(True)
        self.ui.acc_label.setVisible(True)
        self.ui.ip_label.setVisible(True)
        self.ui.pass_label.setVisible(True)

        self.ui.tableWidget.setVisible(False)
        self.ui.up_ptn.setVisible(False)
        self.ui.down_ptn.setVisible(False)
        self.ui.progressBar.setVisible(False)
        self.ui.dir_ptn.setVisible(False)
        self.ui.diredit.setVisible(False)
        self.ui.stop_ptn.setVisible(False)
    def login(self):
        ip=self.ui.ip_edit.text()
        acc=self.ui.acc_edit.text()
        pwd=self.ui.pass_edit.text()
        self.loginobj=login_object(self.controlsocket,ip,acc,pwd)
        self.logthread=QThread()
        self.logthread.started.connect(self.loginobj.connectserver)
        self.endloginobj.connect(self.logthread.quit)
        self.loginobj.endsignal.connect(self.process_connect)
        self.logthread.finished.connect(self.loginobj.deleteLater)
        self.logthread.finished.connect(self.logthread.deleteLater)
        self.loginobj.moveToThread(self.logthread)
        self.logthread.start()

    @pyqtSlot(bool)
    def process_connect(self,result):
        print(1)
        if result:
            print('成功登录')
            self.ip=self.ui.ip_edit.text()
            self.acc=self.ui.acc_edit.text()
            self.pwd=self.ui.pass_edit.text()
            self.mhide()
            self.MLSD()
        else:
            QMessageBox.warning(self,'登录错误','请重新登录',QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
        self.endloginobj.emit()

    def MLSD(self):
        print(2)
        self.datasocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.mlsdthread=QThread()
        self.mlsdobj=mlsd_object(self.ip,self.controlsocket,self.datasocket)
        self.mlsdthread.started.connect(self.mlsdobj.work)
        self.mlsdobj.sendresult.connect(self.process_mlsd)
        self.endmlsdobj.connect(self.mlsdthread.quit)
        self.mlsdthread.finished.connect(self.mlsdobj.deleteLater)
        self.mlsdthread.finished.connect(self.mlsdthread.deleteLater)
        self.mlsdobj.moveToThread(self.mlsdthread)
        self.mlsdthread.start()


    def process_mlsd(self,tag,filelist):
        print(3)
        if tag:
            self.endmlsdobj.emit()
            row=len(filelist)
            self.datasocket.close()
            self.datasocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.ui.tableWidget.setRowCount(row+1)
            self.ui.tableWidget.setColumnCount(4)
            self.ui.tableWidget.verticalHeader().setVisible(False)
            print(filelist)
            headerlist=['name','size(KB)','last modified','permission']
            self.ui.tableWidget.setHorizontalHeaderLabels(headerlist)
            print('get mlsd filepos:\t',self.filepos)
            if self.filepos=='/' or self.filepos=='':
                item=QTableWidgetItem('.')
                item.setFlags(item.flags() & (~Qt.ItemIsEditable))
                self.ui.tableWidget.setItem(0,0,item)
            else:
                item = QTableWidgetItem('..')
                item.setFlags(item.flags() & (~Qt.ItemIsEditable))
                self.ui.tableWidget.setItem(0,0,item)
            onp=1
            for file in filelist:
                self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
                icon=QtGui.QIcon()
                if file['type']=='dir':
                    icon.addFile('icon'+os.sep+'dir.bmp')
                    item=QTableWidgetItem(icon,file['name'])
                    item.setFlags(item.flags()&(~Qt.ItemIsEditable))
                    self.ui.tableWidget.setItem(onp,0,item)

                else:
                     if len(file['name'].split('.'))>=2:
                        icon.addFile('icon'+os.sep+file['name'].split('.')[-1]+'.bmp')
                        item=QTableWidgetItem(icon,file['name'])
                     else:
                         icon.addFile('icon' + os.sep + '0.bmp')
                         item = QTableWidgetItem(icon, file['name'])
                     item.setFlags(item.flags()&(~Qt.ItemIsEditable))
                     self.ui.tableWidget.setItem(onp,0,item)
                     size=float(file['size'])/1024.0
                     size=round(size,2)
                     item = QTableWidgetItem(str(size))
                     item.setFlags(item.flags() & (~Qt.ItemIsEditable))
                     self.ui.tableWidget.setItem(onp,1,item)
                item = QTableWidgetItem(file['perm'])
                item.setFlags(item.flags() & (~Qt.ItemIsEditable))
                self.ui.tableWidget.setItem(onp,2,item)
                item = QTableWidgetItem(processtime(file['modify']))
                item.setFlags(item.flags() & (~Qt.ItemIsEditable))
                self.ui.tableWidget.setItem(onp,3,item)
                onp=onp+1

        else:
            print('获取文件列表失败')
        self.PWD()

    def PWD(self):
        print(4)
        self.pwdthread=QThread()
        self.pwdobj=PWD_Object(self.controlsocket)
        self.pwdthread.started.connect(self.pwdobj.work)
        self.pwdthread.finished.connect(self.pwdobj.deleteLater)
        self.pwdthread.finished.connect(self.pwdthread.deleteLater)
        self.pwdobj.sendpwdreuslt.connect(self.get_pwdresult)
        self.endpwdobj.connect(self.pwdthread.quit)
        self.pwdobj.moveToThread(self.pwdthread)
        self.pwdthread.start()
        print('pwd start')


    def get_pwdresult(self,result):#
        print(5)
        if result!='/':
            self.filepos=result+'/'
        self.endpwdobj.emit()
        print('getpwd filepos:\t',self.filepos,result)
        #self.MLSD()

    def CWD(self,path):
        print(6)
        self.cwdthread=QThread()
        self.cwdobj=CWD_Object(self.controlsocket,path)
        print('cwd path:',path)
        self.cwdthread.started.connect(self.cwdobj.work)
        self.cwdobj.sendcwdreuslt.connect(self.getcwd)
        self.endcwdobj.connect(self.cwdthread.quit)
        self.cwdthread.finished.connect(self.cwdobj.deleteLater)
        self.cwdthread.finished.connect(self.cwdthread.deleteLater)
        self.cwdobj.moveToThread(self.cwdthread)
        self.cwdthread.start()

    def getcwd(self,result):
        print(7)
        self.endcwdobj.emit()
        print('cwd finished,filepos: ', self.filepos)
        if self.filepos!='/':
            self.filepos=result+'/'
        print('cwd finished,filepos: ',self.filepos)
        self.MLSD()






    def process_doubleclick(self,row,col):
        print(8)
        if row==0:
            tmp = self.ui.tableWidget.item(row, 0)
            type = tmp.text()
            print('db filepos:\t',self.filepos)
            if type =='..':
                tmp=self.filepos
                tmp=tmp[0:-2]
                onp=len(tmp)-1
                while onp>1:
                    if tmp[onp]=='/':
                        break
                    onp=onp-1
                self.CWD(tmp[0:onp])
                self.filepos=tmp[0:onp]

        else:
            tmp=self.ui.tableWidget.item(row,2)
            type=tmp.text()[0]
            if type=='d':
                path=self.filepos+self.ui.tableWidget.item(row,0).text()
                print('cwd',path)
                self.CWD(path)
                self.filepos=path
            else:
                self.file=self.filepos+self.ui.tableWidget.item(row,0).text()
                print('set file: ',self.file)


    def MKD(self):
        print(9)
        dirname=self.ui.diredit.text()
        if len(dirname)>0:
            self.mkdobj=MKD_Object(self.controlsocket,self.filepos+dirname)
            self.mkdthread=QThread()
            self.mkdthread.started.connect(self.mkdobj.work)
            self.endmkdobj.connect(self.mkdthread.quit)
            self.mkdthread.finished.connect(self.mkdobj.deleteLater)
            self.mkdthread.finished.connect(self.mkdobj.deleteLater)
            self.mkdobj.sendmkdreuslt.connect(self.get_mkd)
            self.mkdobj.moveToThread(self.mkdthread)
            self.mkdthread.start()


    def get_mkd(self,tag):
        print(10)
        if tag:
            self.endmkdobj.emit()
            self.MLSD()

    def up(self):
        print(11)
        self.working='up'
        self.info = {}
        self.ui.progressBar.setValue(0)
        self.upthread=QThread()
        self.upobj=STOR(self.controlsocket,self.datasocket,self.filepos,self.ip)
        self.upobj.setfilename.connect(self.getfilename)
        self.upthread.started.connect(self.upobj.work)
        self.endupobj.connect(self.upthread.quit)
        self.upthread.finished.connect(self.upobj.deleteLater)
        self.upthread.finished.connect(self.upthread.deleteLater)
        self.upobj.settag.connect(self.gettag)
        self.upobj.endSTOR.connect(self.getup)
        self.upobj.setvalue.connect(self.ui.progressBar.setValue)
        self.upobj.moveToThread(self.upthread)
        self.upthread.start()
        #self.ui.stop_ptn.setVisible(True)

    def getup(self):
        print(12)
        print('上传完成')
        self.endupobj.emit()
        self.MLSD()
        self.ui.progressBar.setValue(100)
        self.ui.stop_ptn.setVisible(False)

    def down(self):
        print(13)
        self.working='down'
        self.info = {}
        self.ui.progressBar.setValue(0)
        self.downobj=RETR(self.controlsocket,self.datasocket,self.ip,self.file)
        self.downthread=QThread()
        #self.ui.stop_ptn.setVisible(True)
        print('mainthread: ',QThread.currentThreadId())
        self.downobj.setfilename.connect(self.getfilename)
        self.downthread.started.connect(self.downobj.work)
        self.downobj.settag.connect(self.gettag)
        self.downobj.enddown.connect(self.getdown)
        self.enddownobj.connect(self.downthread.quit)
        self.downthread.finished.connect(self.downobj.deleteLater)
        self.downthread.finished.connect(self.downthread.deleteLater)
        self.downobj.setvalue.connect(self.ui.progressBar.setValue)
        self.downobj.moveToThread(self.downthread)
        print('ok')
        self.downthread.start()
        #self.ui.retry_ptn.setVisible(True)


    def getdown(self):
        print(14)
        print('getdown')
        self.enddownobj.emit()
        self.ui.progressBar.setValue(100)
        self.ui.stop_ptn.setVisible(False)

    def getfilename(self,local,remote):
        print(15)
        self.localfile=local
        self.remotefile=remote
        print(self.localfile,self.remotefile)

    def gettag(self,tag):
        self.tag=tag
    @pyqtSlot()
    def mstop(self):
        if self.working=='down':
            self.downobj.mutex.lock()
            self.downobj.tag=False
            self.downobj.mutex.unlock()
        elif self.working=='up':
            self.upobj.mutex.lock()
            self.upobj.tag=False
            self.downobj.mutex.unlock()
        else:
            pass
        if self.working=='down' or self.working=='up':
            #self.ui.retry_ptn.setVisible(True)
            print(self.working,'size:',self.tag,'local file:',self.localfile,'remote file:',self.remotefile)
            self.info['working']=self.working
            self.info['size']=self.tag
            self.info['localfile']=self.localfile
            self.info['remotefile']=self.remotefile

    def retry(self):
        print('test retry')
        if self.info !={}:
            print('test')
            print('test retry',self.info['working'])
            if self.info['working']=='up':
                self.working = 'up'
                self.upthread = QThread()
                self.upobj = STOR(self.controlsocket, self.datasocket, self.filepos,
                                  self.ip,retry=True,offset=self.tag,localfile=self.info['localfile'])
                self.upobj.setfilename.connect(self.getfilename)

                self.upthread.started.connect(self.upobj.work)
                self.endupobj.connect(self.upthread.quit)
                self.upthread.finished.connect(self.upobj.deleteLater)
                self.upthread.finished.connect(self.upthread.deleteLater)
                self.upobj.settag.connect(self.gettag)
                self.upobj.endSTOR.connect(self.getup)
                self.upobj.setvalue.connect(self.ui.progressBar.setValue)
                self.upobj.moveToThread(self.upthread)
                self.upthread.start()
                #self.ui.stop_ptn.setVisible(True)
            elif self.info['working']=='down':
                self.downobj = RETR(self.controlsocket, self.datasocket, self.ip, self.file
                                    ,retry=True,offset=self.tag,localfile=self.info['localfile'])
                self.downthread = QThread()
                #self.ui.stop_ptn.setVisible(True)
                self.downobj.setfilename.connect(self.getfilename)
                self.downthread.started.connect(self.downobj.work)
                self.downobj.settag.connect(self.gettag)
                self.downobj.enddown.connect(self.getdown)
                self.enddownobj.connect(self.downthread.quit)
                self.downthread.finished.connect(self.downobj.deleteLater)
                self.downthread.finished.connect(self.downthread.deleteLater)
                self.downobj.setvalue.connect(self.ui.progressBar.setValue)
                self.downobj.moveToThread(self.downthread)
                self.downthread.start()





if __name__=='__main__':
    app=QApplication(sys.argv)
    wid=mainwidget()
    wid.show()
    sys.exit(app.exec_())