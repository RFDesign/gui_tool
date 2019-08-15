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
from ..widgets.disable_port import DisablePort
from ..widgets.disable_port_node_monitor import NodeMonitorWidget

__all__ = 'PANEL_NAME', 'spawn', 'get_icon'

PANEL_NAME = 'Disable Node Panel'


logger = getLogger(__name__)

_singleton = None


#The flight controller emulator panel form
class DisableNodePanel(QDialog):
    DEFAULT_INTERVAL = 0.1

    def __init__(self, parent, node):
        super(DisableNodePanel, self).__init__(parent)
        self.setWindowTitle('Disable CAN Panel')
        self.setAttribute(Qt.WA_DeleteOnClose)              # This is required to stop background timers!

        self._node = node

        layout = QVBoxLayout(self)

        logger.info('Creating node monitor')
        self._disable_monitor = NodeMonitorWidget(self, node)
        self._disable_monitor.AllNodesDeselected.connect(self.node_table_all_nodes_deselected)
        self._disable_monitor.NodeSelected.connect(self.node_table_node_selected)
        
        logger.info('Creating Disable port')
        self._disable_port = DisablePort(self)
        self._disable_port.setEnabled(False)
        self._disable_port.Go.connect(self.enable_disable_ports)

        logger.info('Add monitor widget')

        layout.addWidget(self._disable_monitor)
        logger.info('Add dis port widget')
        layout.addWidget(self._disable_port)

        logger.info('Setting layout')

        self.setLayout(layout)
        logger.info('Resizing')
        #self.resize(self.minimumWidth(), self.minimumHeight())
        logger.info('Resized')

    def __del__(self):
        global _singleton
        _singleton = None

    def closeEvent(self, event):
        global _singleton
        _singleton = None
        super(DisableNodePanel, self).closeEvent(event)
        
    def node_table_all_nodes_deselected(self):
        logger.info('All nodes deselected')
        self._disable_port.setEnabled(False)
        
    def node_table_node_selected(self, nid):
        logger.info(str(nid) + ' selected')
        self._disable_port.setEnabled(True)
        self._nidselected = nid
        self._disable_port.SetNodeID(nid)
        
    def enable_disable_ports(self):
        if (self._node.is_anonymous):
            self._disable_port.SetMsg('Cannot do in anonymous mode.  Set a local node ID')
        else:
            logger.info('Enabling/disabling ' + str(self._nidselected))
            msg = uavcan.thirdparty.rfd.af3.IgnoreCANPort()
            msg.NodeID = self._nidselected
            msg.IgnoreCANPort = self._disable_port.GetEnabledArray()
            self._node.broadcast(msg)
            self._disable_port.SetMsg(uavcan.to_yaml(msg))

def spawn(parent, node):
    global _singleton
    if _singleton is None:
        _singleton = DisableNodePanel(parent, node)

    _singleton.show()
    _singleton.raise_()
    _singleton.activateWindow()

    return _singleton


get_icon = partial(get_icon, 'asterisk')
