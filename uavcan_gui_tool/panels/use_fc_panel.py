#
# Copyright (C) 2016  UAVCAN Development Team  <uavcan.org>
#
# This software is distributed under the terms of the MIT License.
#
# Author: Pavel Kirienko <pavel.kirienko@zubax.com>
#

import uavcan
from functools import partial
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QDialog, QSlider, QSpinBox, QDoubleSpinBox, \
    QPlainTextEdit
from PyQt5.QtCore import QTimer, Qt
from logging import getLogger
from ..widgets import make_icon_button, get_icon, get_monospace_font
from PyQt5.Qt import QPushButton

__all__ = 'PANEL_NAME', 'spawn', 'get_icon'

PANEL_NAME = 'Use FC Panel'

logger = getLogger(__name__)

_singleton = None


class UseFCPanel(QDialog):
    DEFAULT_INTERVAL = 0.1

    def __init__(self, parent, node):
        super(UseFCPanel, self).__init__(parent)
        self.setWindowTitle('Use FC Panel')
        self.setAttribute(Qt.WA_DeleteOnClose)              # This is required to stop background timers!

        self._node = node
        
        self._btn_use_this = QPushButton('Use this')
        self._btn_use_this.clicked.connect(self._use_this)
        
        self._btn_use_other = QPushButton("Don't use this")
        self._btn_use_other.clicked.connect(self._use_other)

        layout = QVBoxLayout(self)
        
        hlayout = QHBoxLayout(self)

        hlayout.addWidget(self._btn_use_this)
        hlayout.addWidget(self._btn_use_other)
        
        self._msg_viewer = QPlainTextEdit(self)
        self._msg_viewer.setReadOnly(True)
        self._msg_viewer.setLineWrapMode(QPlainTextEdit.NoWrap)
        self._msg_viewer.setFont(get_monospace_font())
        self._msg_viewer.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._msg_viewer.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        layout.addLayout(hlayout)
        layout.addWidget(self._msg_viewer)

        self.setLayout(layout)
        self.resize(self.minimumWidth(), self.minimumHeight())

    def _use_this(self):
        self._send_use_fc(1, 1, 1)
        
    def _use_other(self):
        self._send_use_fc(1, 2, 1)
        
    def _send_use_fc(self, thisbus, usefcbus, uniqueid):
        try:
            msg = uavcan.thirdparty.rfd.af3.UseFlightController()
            msg.UniqID = uniqueid
            msg.UseFConBus = usefcbus
            msg.ThisBus = thisbus
            self._node.broadcast(msg)
            self._msg_viewer.setPlainText(uavcan.to_yaml(msg))
        except Exception as ex:
            self._msg_viewer.setPlainText('Publishing failed:\n' + str(ex))

    def __del__(self):
        global _singleton
        _singleton = None

    def closeEvent(self, event):
        global _singleton
        _singleton = None
        super(UseFCPanel, self).closeEvent(event)


def spawn(parent, node):
    global _singleton
    if _singleton is None:
        _singleton = UseFCPanel(parent, node)

    _singleton.show()
    _singleton.raise_()
    _singleton.activateWindow()

    return _singleton


get_icon = partial(get_icon, 'asterisk')
