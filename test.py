from PyQt5 import Qt,QtGui,QtWidgets,QtCore
import  sys
import os
if __name__=='__main__':
    getlist=[]
    emptylist=[]
    app=QtWidgets.QApplication(sys.argv)
    label=QtWidgets.QPushButton()
    # fileInfo = Qt.QFileInfo('E:\\pyproject\\myftp\\')
    # fileIcon = Qt.QFileIconProvider()
    # icon = QtGui.QIcon(fileIcon.icon(fileInfo))
    # label.setIcon(icon)
    # tmp=icon.pixmap(QtCore.QSize(20,20))
    # tmp.save('dir.bmp')

    # for path,dir_list,file_list in os.walk('E:\\'):
    #     for file in file_list:
    #         if len(file.split('.'))>=2:
    #             if file.split('.')[-1] not in getlist:
    #                 getlist.append(file.split('.')[-1])
    #                 if path=='E:\\':
    #                     fileInfo = Qt.QFileInfo(path+file)
    #                 else:
    #                     fileInfo = Qt.QFileInfo(path+os.sep+file)
    #                 fileIcon = Qt.QFileIconProvider()
    #                 icon = QtGui.QIcon(fileIcon.icon(fileInfo))
    #                 tmp=icon.pixmap(Qt.QSize(500,500))
    #                 tmp.save('icon'+os.sep+file.split('.')[-1]+'.bmp')
    #                 if tmp.width()==0 or tmp.height()==0:
    #                     emptylist.append(file.split('.')[-1])
    #                     emptylist.append(path+os.sep+file)
    # print(len(getlist))
    # print(emptylist)
    # for path,dir_list,file_list in os.walk('F:\\'):
    #     for file in file_list:
    #         if len(file.split('.'))>=2:
    #             if file.split('.')[-1] not in getlist:
    #                 getlist.append(file.split('.')[-1])
    #                 fileInfo = Qt.QFileInfo(path+os.sep+file)
    #                 fileIcon = Qt.QFileIconProvider()
    #                 icon = QtGui.QIcon(fileIcon.icon(fileInfo))
    #                 tmp=icon.pixmap(Qt.QSize(500,500))
    #                 tmp.save('icon'+os.sep+file.split('.')[-1]+'.bmp')
    #                 if tmp.width()==0 or tmp.height()==0:
    #                     emptylist.append(file.split('.')[-1])
    #                     emptylist.append(path + os.sep + file)
    # for path,dir_list,file_list in os.walk('C:\\'):
    #     for file in file_list:
    #         if len(file.split('.'))>=2:
    #             if file.split('.')[-1] not in getlist:
    #                 getlist.append(file.split('.')[-1])
    #                 fileInfo = Qt.QFileInfo(path+os.sep+file)
    #                 fileIcon = Qt.QFileIconProvider()
    #                 icon = QtGui.QIcon(fileIcon.icon(fileInfo))
    #                 tmp=icon.pixmap(Qt.QSize(500,500))
    #                 tmp.save('icon'+os.sep+file.split('.')[-1]+'.bmp')
    #                 if tmp.width()==0 or tmp.height()==0:
    #                     emptylist.append(file.split('.')[-1])
    #                     emptylist.append(path + os.sep + file)
    # print(len(getlist))
    # print(emptylist)
    label.show()
    sys.exit(app.exec_())