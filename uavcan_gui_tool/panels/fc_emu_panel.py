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

__all__ = 'PANEL_NAME', 'spawn', 'get_icon'

PANEL_NAME = 'FC Emu Panel'


logger = getLogger(__name__)

_singleton = None


class PercentSlider(QWidget):
    def __init__(self, parent):
        super(PercentSlider, self).__init__(parent)

        self._slider = QSlider(Qt.Vertical, self)
        self._slider.setMinimum(0)
        self._slider.setMaximum(100)
        self._slider.setValue(100)
        self._slider.setTickInterval(10)
        self._slider.setTickPosition(QSlider.TicksBothSides)
        self._slider.valueChanged.connect(lambda: self._spinbox.setValue(self._slider.value()/100))

        #self._label = QLabel(self)

        self._spinbox = QDoubleSpinBox(self)
        self._spinbox.setMinimum(0)
        self._spinbox.setMaximum(1)
        self._spinbox.setValue(1)
        self._spinbox.setSingleStep(0.01)
        self._spinbox.valueChanged.connect(lambda: self._slider.setValue(self._spinbox.value()*100))

        self._default_button = make_icon_button('hand-stop-o', 'Default setpoint', self, on_clicked=self.default)

        layout = QVBoxLayout(self)
        sub_layout = QHBoxLayout(self)
        sub_layout.addStretch()
        sub_layout.addWidget(self._slider)
        sub_layout.addStretch()
        layout.addLayout(sub_layout)
        layout.addWidget(self._spinbox)
        layout.addWidget(self._default_button)
        self.setLayout(layout)

        self.setMinimumHeight(400)

    def default(self):
        self._slider.setValue(100)

    def get_value(self):
        return self._slider.value()/100

#The flight controller emulator panel form
class FCEMUPanel(QDialog):
    DEFAULT_INTERVAL = 0.1

    def __init__(self, parent, node):
        super(FCEMUPanel, self).__init__(parent)
        self.setWindowTitle('FC Emu. Panel')
        self.setAttribute(Qt.WA_DeleteOnClose)              # This is required to stop background timers!

        self._node = node

        self._slider = PercentSlider(self)

        self._bcast_interval = QDoubleSpinBox(self)
        self._bcast_interval.setMinimum(0.01)
        self._bcast_interval.setMaximum(1.0)
        self._bcast_interval.setSingleStep(0.1)
        self._bcast_interval.setValue(self.DEFAULT_INTERVAL)
        self._bcast_interval.valueChanged.connect(
            lambda: self._bcast_timer.setInterval(self._bcast_interval.value() * 1e3))

        self._stop_all = make_icon_button('hand-stop-o', 'Zero all channels', self, text='Stop All',
                                          on_clicked=self._do_stop_all)

        self._pause = make_icon_button('pause', 'Pause publishing', self, checkable=True, text='Pause')

        self._msg_viewer = QPlainTextEdit(self)
        self._msg_viewer.setReadOnly(True)
        self._msg_viewer.setLineWrapMode(QPlainTextEdit.NoWrap)
        self._msg_viewer.setFont(get_monospace_font())
        self._msg_viewer.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._msg_viewer.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self._bcast_timer = QTimer(self)
        self._bcast_timer.start(self.DEFAULT_INTERVAL * 1e3)
        self._bcast_timer.timeout.connect(self._do_broadcast)

        layout = QVBoxLayout(self)

        self._slider_layout = QHBoxLayout(self)
        self._slider_layout.addWidget(self._slider)
        layout.addLayout(self._slider_layout)

        layout.addWidget(self._stop_all)

        controls_layout = QHBoxLayout(self)
 #       controls_layout.addWidget(QLabel('Channels:', self))
 #       controls_layout.addWidget(self._num_sliders)
        controls_layout.addWidget(QLabel('Broadcast interval:', self))
        controls_layout.addWidget(self._bcast_interval)
        controls_layout.addWidget(QLabel('sec', self))
        controls_layout.addStretch()
        controls_layout.addWidget(self._pause)
        layout.addLayout(controls_layout)

        layout.addWidget(QLabel('Generated message:', self))
        layout.addWidget(self._msg_viewer)

        self.setLayout(layout)
        self.resize(self.minimumWidth(), self.minimumHeight())

    def _do_broadcast(self):
        try:
            if not self._pause.isChecked():
                msg = uavcan.thirdparty.rfd.af3.FlightControllerHealth()
                msg.ErrorScore = 1 - self._slider.get_value();
                 
                self._node.broadcast(msg)
                self._msg_viewer.setPlainText(uavcan.to_yaml(msg))
            else:
                self._msg_viewer.setPlainText('Paused')
        except Exception as ex:
            self._msg_viewer.setPlainText('Publishing failed:\n' + str(ex))

    def _do_stop_all(self):
        self._slider.default()

    def __del__(self):
        global _singleton
        _singleton = None

    def closeEvent(self, event):
        global _singleton
        _singleton = None
        super(FCEMUPanel, self).closeEvent(event)


def spawn(parent, node):
    global _singleton
    if _singleton is None:
        _singleton = FCEMUPanel(parent, node)

    _singleton.show()
    _singleton.raise_()
    _singleton.activateWindow()

    return _singleton


get_icon = partial(get_icon, 'asterisk')
