

from PyQt5.QtWidgets import QWidget, QCheckBox, QPushButton
from PyQt5.Qt import QHBoxLayout, pyqtSignal

class DisablePort(QWidget):
    Go = pyqtSignal()
    
    def on_go(self):
        self.Go.emit()
    
    def __init__(self, parent):
        super(DisablePort, self).__init__(parent)
        
        layout = QHBoxLayout()
        self._check0 = QCheckBox('Bus 0')
        self._check0.setChecked(True)
        layout.addWidget(self._check0)
        
        self._check1 = QCheckBox('Bus 1')
        self._check1.setChecked(True)
        layout.addWidget(self._check1)
        
        self._check2 = QCheckBox('Bus 2')
        self._check2.setChecked(True)
        layout.addWidget(self._check2)
        
        self._Go = QPushButton('Enable/Disable Ports')
        self._Go.clicked.connect(self.on_go)
        layout.addWidget(self._Go)
        
        self.setLayout(layout)

    def GetEnable(self):
        return [self._check0.isChecked(), self._check1.isChecked(), self._check2.isChecked()]
    
