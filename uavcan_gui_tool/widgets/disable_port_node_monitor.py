#
# Copyright (C) 2016  UAVCAN Development Team  <uavcan.org>
#
# This software is distributed under the terms of the MIT License.
#
# Author: Pavel Kirienko <pavel.kirienko@zubax.com>
#

#
# This is the main list of nodes on the main window.
#

# com.rfd.arbiter
# com.rfd.endpoint

import datetime
import uavcan
from . import BasicTable, get_monospace_font
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHeaderView, QLabel
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from logging import getLogger
from PyQt5.Qt import QCheckBox


logger = getLogger(__name__)


def node_mode_to_color(mode):
    s = uavcan.protocol.NodeStatus()
    return {
        s.MODE_INITIALIZATION: Qt.cyan,
        s.MODE_MAINTENANCE: Qt.magenta,
        s.MODE_SOFTWARE_UPDATE: Qt.magenta,
        s.MODE_OFFLINE: Qt.red
    }.get(mode)


def node_health_to_color(health):
    s = uavcan.protocol.NodeStatus()
    return {
        s.HEALTH_WARNING: Qt.yellow,
        s.HEALTH_ERROR: Qt.magenta,
        s.HEALTH_CRITICAL: Qt.red,
    }.get(health)


def render_vendor_specific_status_code(s):
    out = '%-5d     0x%04x\n' % (s, s)
    binary = bin(s)[2:].rjust(16, '0')

    def high_nibble(s):
        return s.replace('0', '\u2070').replace('1', '\u00B9')  # Unicode 0/1 superscript

    def low_nibble(s):
        return s.replace('0', '\u2080').replace('1', '\u2081')  # Unicode 0/1 subscript

    nibbles = [
        high_nibble(binary[:4]),
        low_nibble(binary[4:8]),
        high_nibble(binary[8:12]),
        low_nibble(binary[12:]),
    ]

    out += ''.join(nibbles)
    return out

class DisTableNode:
    def __init__(self, nid, name, talking):
        self.nid = nid
        self.name = name
        self.talking = talking
        self.can = None
        
class DisTableSession:
    def __init__(self, node):
        self._node = node
        self._monitor = uavcan.app.node_monitor.NodeMonitor(node)
        self._remembered = dict()
    
    def GetAllNodes(self, filter):
        known_nodes = {e.node_id: e for e in self._monitor.find_all(lambda _: True)}
        for nid in known_nodes.keys():
            if self._remembered.__contains__(nid):
                self._remembered[nid].name = known_nodes[nid].info.name
                self._remembered[nid].talking = True
            else:
                self._remembered[nid] = DisTableNode(nid, known_nodes[nid].info.name if known_nodes[nid].info else '?', True)
    
        for nid in self._remembered.keys():
            if not known_nodes.__contains__(nid):
                self._remembered[nid].talking = False
                
        if not self._remembered.__contains__(0):
            self._remembered[0] = DisTableNode(0, 'Everything', False)
        
        if filter:
            result = dict()
            for nid in self._remembered.keys():
                #logger.info('Checking if ' + str(self._remembered[nid].name) + ' contains.')
                if ('com.rfd.arbiter' in str(self._remembered[nid].name)) or ('com.rfd.endpoint' in str(self._remembered[nid].name)):
                    result[nid] = self._remembered[nid]
            result[0] = self._remembered[0]
            
            return result
        else:
            return self._remembered
    
    def close(self):
        self._monitor.close()
        
    def set_node_CAN_Status(self, nid, can):
        if nid == 0:
            for id in self._remembered.keys():
                self._remembered[id].can = can
        else:
            if self._remembered.__contains__(nid):
                self._remembered[nid].can = can

class NodeTable(BasicTable):
    filter_checkbox = None
    COLUMNS = [
        BasicTable.Column('NID',
                          lambda e: e.nid),
        BasicTable.Column('Name',
                          lambda e: e.name,
                          QHeaderView.Stretch),
        BasicTable.Column('Talking',
                          lambda e: e.talking),
        BasicTable.Column('CAN 0',
                          lambda e: str(e.can[0]) if (e.can != None) else '?'),
        BasicTable.Column('CAN 1',
                          lambda e: str(e.can[1]) if (e.can != None) else '?'),
        BasicTable.Column('CAN 2',
                          lambda e: str(e.can[2]) if (e.can != None) else '?'),
    ]

    info_requested = pyqtSignal([int])

    def __init__(self, parent, node):
        super(NodeTable, self).__init__(parent, self.COLUMNS, font=get_monospace_font())

        self._session = DisTableSession(node)

        self._timer = QTimer(self)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self._update)
        self._timer.start(500)

        self.setMinimumWidth(600)

        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def set_node_CAN_Status(self, nid, can):
        self._session.set_node_CAN_Status(nid, can)

    def close(self):
        self._monitor.close()

    def get_node_ids_selected(self):
        res = []
        for si in self.selectionModel().selectedRows():
            res.append(int(self.item(si.row(), 0).text()))
        return res

    def _update(self):
        filter = True
        if self.filter_checkbox != None:
            filter = self.filter_checkbox.isChecked()
        known_nodes = self._session.GetAllNodes(filter)
        displayed_nodes = set()
        rows_to_remove = []

        # Updating existing entries
        for row in range(self.rowCount()):
            nid = int(self.item(row, 0).text())
            displayed_nodes.add(nid)
            if nid not in known_nodes:
                rows_to_remove.append(row)
            else:
                self.set_row(row, known_nodes[nid])

        # Removing nonexistent entries
        for row in rows_to_remove[::-1]:     # It is important to traverse from end
            logger.info('Removing row %d', row)
            self.removeRow(row)

        # Adding new entries
        def find_insertion_pos_for_node_id(target_nid):
            for row in range(self.rowCount()):
                nid = int(self.item(row, 0).text())
                if nid > target_nid:
                    return row
            return self.rowCount()

        for nid in set(known_nodes.keys()) - displayed_nodes:
            row = find_insertion_pos_for_node_id(nid)
            logger.info('Adding new row %d for node %d', row, nid)
            self.insertRow(row)
            self.set_row(row, known_nodes[nid])


class NodeMonitorWidget(QGroupBox):
    AllNodesDeselected = pyqtSignal()
    NodeSelected = pyqtSignal(int)
    
    def __init__(self, parent, node):
        super(NodeMonitorWidget, self).__init__(parent)
        self.setTitle('Nodes')

        self._node = node
        self.on_info_window_requested = lambda *_: None

        logger.info('Creating update timer')

        #self._status_update_timer = QTimer(self)
        #self._status_update_timer.setSingleShot(False)
        #self._status_update_timer.timeout.connect(self._update_status)
        #self._status_update_timer.start(500)

        logger.info('Creating NodeTable')
        self._table = NodeTable(self, node)
        self._table.info_requested.connect(self._show_info_window)
        self._table.itemSelectionChanged.connect(self.node_table_item_changed)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self._table)
        
        self._namefilter = QCheckBox('Show only nodes whose name contains com.rfd.arbiter or com.rfd.endpoint')
        self._namefilter.setChecked(True)
        vbox.addWidget(self._namefilter)
        self._table.filter_checkbox = self._namefilter
        
        self.setLayout(vbox)
        
    @property
    def monitor(self):
        return self._table.monitor
    
    def set_node_CAN_Status(self, nid, can):
        self._table.set_node_CAN_Status(nid, can)
    
    def node_table_item_changed(self):
        logger.info('Item changed')
        for ni in self._table.get_node_ids_selected():
            logger.info(ni)
        ids = self._table.get_node_ids_selected()
        if (len(ids) == 0):
            self.AllNodesDeselected.emit()
        else:
            self.NodeSelected.emit(ids[0])

    def close(self):
        self._table.close()
        self._monitor_handle.remove()
        self._status_update_timer.stop()

    def _show_info_window(self, node_id):
        self.on_info_window_requested(node_id)
