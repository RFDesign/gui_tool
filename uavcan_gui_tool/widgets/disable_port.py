

from PyQt5.QtWidgets import QWidget, QCheckBox, QPushButton, QPlainTextEdit
from PyQt5.Qt import QHBoxLayout, pyqtSignal, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt
from . import make_icon_button, get_icon, get_monospace_font

class DisablePort(QWidget):
    Go = pyqtSignal()
    
    def on_go(self):
        self.Go.emit()
    
    def __init__(self, parent):
        super(DisablePort, self).__init__(parent)
        
        layout = QHBoxLayout()
        self._check0 = QCheckBox('CAN 0')
        self._check0.setChecked(True)
        layout.addWidget(self._check0)
        
        self._check1 = QCheckBox('CAN 1')
        self._check1.setChecked(True)
        layout.addWidget(self._check1)
        
        self._check2 = QCheckBox('CAN 2')
        self._check2.setChecked(True)
        layout.addWidget(self._check2)
        
        self._Go = QPushButton('Enable CAN Ports')
        self._Go.clicked.connect(self.on_go)
        layout.addWidget(self._Go)
        
        layout2 = QVBoxLayout()
        layout2.addLayout(layout)
        
        self._msg_viewer = QPlainTextEdit(self)
        self._msg_viewer.setReadOnly(True)
        self._msg_viewer.setLineWrapMode(QPlainTextEdit.NoWrap)
        self._msg_viewer.setFont(get_monospace_font())
        self._msg_viewer.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._msg_viewer.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout2.addWidget(self._msg_viewer)
        
        self.setLayout(layout2)

    def GetEnable(self):
        return [self._check0.isChecked(), self._check1.isChecked(), self._check2.isChecked()]
    
    def SetNodeID(self, nid):
        self._Go.setText('Enable CAN Ports on ' + str(nid))
        #self._check0.setChecked(isChecked[0] if (isChecked != None) else True)
        #self._check1.setChecked(isChecked[1] if (isChecked != None) else True)
        #self._check2.setChecked(isChecked[2] if (isChecked != None) else True)
    
    def SetMsg(self, msg):
        self._msg_viewer.setPlainText(msg)
        
    def GetEnabledArray(self):
        return [self._check0.isChecked(), self._check1.isChecked(), self._check2.isChecked()]
    
