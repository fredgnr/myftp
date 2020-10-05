from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFileDialog
import socket
import time
def process_MLSD(string):
    files=string.decode('gbk')
    filelist=files.strip().split('\r\n')
    if '' in filelist:
        filelist.remove('')
    result=[]
    dirlist=[]
    typefilelist=[]
    for item in filelist:
        itemlist=item.split(';')
        tmp = {}
        if len(itemlist)==4: #文件夹
            tmp['type']='dir'
            tmp['perm']=itemlist[1].split('=')[-1]
            tmp['modify']=itemlist[2].split('=')[-1]
            tmp['name']=itemlist[3].strip()
            dirlist.append(tmp)
        else:
            tmp['type'] = 'file'
            tmp['perm'] = itemlist[1].split('=')[-1]
            tmp['size']=int(itemlist[3].split('=')[-1])
            tmp['modify'] = itemlist[2].split('=')[-1]
            tmp['name'] = itemlist[4].strip()
            typefilelist.append(tmp)
    result=dirlist+typefilelist
    return result
class login_object(QObject):
    endsignal = pyqtSignal(bool)
    def __init__(self,clientsock,ip,name,pwd,parent=None):
        super().__init__(parent)
        self.clientsock=clientsock
        self.ip=ip
        self.name=name
        self.pwd=pwd
    @pyqtSlot()
    def connectserver(self):
        try:
            tag=False
            self.clientsock.connect((self.ip, 21))
            cmd=self.clientsock.recv(1024)
            tmp = cmd.decode()
            tmplist = tmp.strip().split('\r\n')
            if int(tmp.split()[0]) == 220:
                for item in tmplist:
                    print(item)
            self.clientsock.sendall(('USER '+self.name+'\r\n').encode())  # 发送用户名
            cmd = self.clientsock.recv(1024)
            cmd = cmd.decode()
            if int(cmd[0:3]) == 331:
                self.clientsock.sendall(('PASS '+self.pwd+'\r\n').encode())
                cmd = self.clientsock.recv(1024)
                if int(cmd[0:3]) == 230:
                    tag=True
            if tag:
                self.endsignal.emit(True)
            else:
                self.endsignal.emit(False)
        except Exception:
            print('error')
            self.endsignal.emit(False)
class mlsd_object(QObject):
    sendresult=pyqtSignal(bool,list)
    def __init__(self,ip,controlsocket,datasocket,parent=None):
        super().__init__(parent)
        self.controlsocket=controlsocket
        self.datasocket=datasocket
        self.ip=ip
    def work(self):
        self.controlsocket.sendall('PASV \r\n'.encode())
        cmd = self.controlsocket.recv(1024)  # 接收端口
        cmd = cmd.decode()
        start = cmd.find('(')
        end = cmd.find(')')
        sub = cmd[start + 1:end]
        sublist = sub.split(',')
        port = int(sublist[-2]) * 256 + int(sublist[-1])
        self.datasocket.connect((self.ip,port))
        self.controlsocket.sendall('MLSD\r\n'.encode())
        tmp=self.controlsocket.recv(1024)
        if tmp.decode()[0:3]=='150':
            cmd=self.datasocket.recv(1024*1000)
            resultlist=process_MLSD(cmd)
            self.sendresult.emit(True,resultlist)
            cmd=self.controlsocket.recv(1024)
        else:
            self.sendresult.emit(False,[])
        self.datasocket.close()


def processtime(time):
    s=time[0:4]+'-'+time[4:6]+'-'+time[6:8]+' '+time[8:10]+':'+time[10:12]
    return s


class PWD_Object(QObject):
    sendpwdreuslt=pyqtSignal(str)
    def __init__(self,controlsocket,parent=None):
        super().__init__(parent)
        self.controlsocket=controlsocket
        print('ok')

    def work(self):
        self.controlsocket.sendall('PWD \r\n'.encode())
        cmd=self.controlsocket.recv(1024)
        cmd=cmd.decode('gbk')
        if int(cmd[0:3])==257:
            cmdlist=cmd.split('\"')
            result=cmdlist[1]
            print(result)
            self.sendpwdreuslt.emit(result)

class CWD_Object(QObject):
    sendcwdreuslt=pyqtSignal(str)
    def __init__(self,controlsocket,path,parent=None):
        super().__init__(parent)
        self.controlsocket=controlsocket
        self.path=path

    def work(self):
        self.controlsocket.sendall(('CWD '+self.path+'\r\n').encode())
        cmd=self.controlsocket.recv(1024)
        cmd=cmd.decode('gbk')
        print(cmd)
        if int(cmd[0:3])==250:
            cmdlist=cmd.split('\"')
            result=cmdlist[1]
            print(result)
            self.sendcwdreuslt.emit(result)

class MKD_Object(QObject):
    sendmkdreuslt=pyqtSignal(bool)
    def __init__(self,controlsocket,path,parent=None):
        super().__init__(parent)
        self.controlsocket=controlsocket
        self.path=path

    def work(self):
        self.controlsocket.sendall(('MKD '+self.path+'\r\n').encode())
        cmd=self.controlsocket.recv(1024)
        cmd=cmd.decode('gbk')
        print(cmd)
        if int(cmd[0:3])==257:
            self.sendmkdreuslt.emit(True)
        else:
            self.sendmkdreuslt.emit(False)
import os
class STOR(QObject):
    endSTOR=pyqtSignal()
    setvalue=pyqtSignal(int)
    setfilename=pyqtSignal(str,str)
    settag=pyqtSignal(int)
    def __init__(self,controlsocket,datasocket,path,ip,retry=False,offset=0,localfile='',parent=None):
        super().__init__(parent)
        self.controlsocket=controlsocket
        self.datasocket=datasocket
        self.path=path
        self.ip=ip
        self.localfile=localfile
        self.retry=retry
        self.offset=offset
        self.mutex=QMutex()
        self.tag=True
    @pyqtSlot()
    def work(self):
        url=QFileDialog.getOpenFileName()
        print(url)
        filename=url[0].split('/')[-1]
        print('filename:\t',filename)
        if self.retry:
            url[0]=self.localfile
        with open(url[0],'rb') as f:
            self.controlsocket.sendall('PASV \r\n'.encode())
            cmd = self.controlsocket.recv(1024)  # 接收端口
            cmd = cmd.decode()
            start = cmd.find('(')
            end = cmd.find(')')
            sub = cmd[start + 1:end]
            sublist = sub.split(',')
            port = int(sublist[-2]) * 256 + int(sublist[-1])
            if self.retry:
                self.controlsocket.sendall(('C ' + str(self.offset)+ '\r\n').encode())
                cmd=self.controlsocket.recv(1024)
                print(cmd)
                f.seek(self.offset)
            self.datasocket.connect((self.ip, port))
            self.controlsocket.sendall(('STOR '+self.path+filename+'\r\n').encode())
            self.setfilename.emit(url[0],self.path+filename)
            size=os.path.getsize(url[0])
            cmd=self.controlsocket.recv(1024)
            tmp=size
            size=size-self.offset
            if int(cmd[0:3])==150:
                self.mutex.lock()
                while size>0 and self.tag:
                    self.mutex.unlock()
                    self.datasocket.sendall(f.read(4096))
                    size=size-4096
                    self.settag.emit(tmp-size)
                    self.setvalue.emit(float(tmp-size)/float(tmp)*100.0)
                    self.mutex.lock()
                self.mutex.unlock()
            self.datasocket.close()
            cmd=self.controlsocket.recv(1024)
            print(cmd)
            self.endSTOR.emit()


class RETR(QObject):
    enddown=pyqtSignal()
    setvalue=pyqtSignal(int)
    setfilename=pyqtSignal(str,str)
    settag=pyqtSignal(int)
    def __init__(self,controlsocket,datasocket,ip,filename,retry=False,offset=0,localfile='',parent=None):
        super().__init__(parent)
        self.controlsocket=controlsocket
        self.datasocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.ip=ip
        self.localfile=localfile
        self.filename=filename
        self.tag=True
        self.mutex=QMutex()
        self.retry=retry
        self.offset=offset

    @pyqtSlot()
    def work(self):
        print(1)
        if self.retry:
            tmp=self.localfile
            QThread.sleep(1)
        else:
            path=QFileDialog.getExistingDirectory()
            print('path: ',path)
            tmp=path+'/'+self.filename.split('/')[-1]
        print(2)
        with open(tmp,'wb') as f:
            #print('下载文件：',path+os.sep+self.filename.split('/')[-1],self.filename)
            self.controlsocket.sendall('PASV \r\n'.encode())
            cmd = self.controlsocket.recv(1024)  # 接收端口
            cmd = cmd.decode()
            print(3)
            start = cmd.find('(')
            end = cmd.find(')')
            sub = cmd[start + 1:end]
            sublist = sub.split(',')
            port = int(sublist[-2]) * 256 + int(sublist[-1])
            self.datasocket.connect((self.ip, port))
            self.controlsocket.sendall(('SIZE '+self.filename+'\r\n').encode())
            cmd=self.controlsocket.recv(1024)
            cmd=cmd.decode()
            size=cmd.split(' ')
            size=int(size[-1])
            print('size: ',size)
            tmp=size
            tmp=tmp-self.offset
            print(4)
            if self.retry:
                print('retry')
                self.controlsocket.sendall(('REST '+str(self.offset)+'\r\n').encode())
                cmd=self.controlsocket.recv(1024)
                f.seek(self.offset)
            print(cmd)
            self.controlsocket.sendall(('RETR '+self.filename+'\r\n').encode())
            self.setfilename.emit(path+'/'+self.filename.split('/')[-1],self.filename)
            cmd=self.controlsocket.recv(1024)
            print(cmd)
            self.mutex.lock()
            print(5)
            while tmp>0 and self.tag:
                self.mutex.unlock()
                cmd=self.datasocket.recv(4096)
                f.write(cmd)
                self.settag.emit(size-tmp)
                tmp=tmp-4096
                self.setvalue.emit(float(size-tmp)/float(size)*100.0)
                self.mutex.lock()
            self.mutex.unlock()
            cmd=self.controlsocket.recv(1024)
            if self.tag:
                self.datasocket.close()
                cmd=self.controlsocket.recv(1024)
                print('tag ')
            print(cmd)
        self.enddown.emit()







