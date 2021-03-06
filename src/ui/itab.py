# coding=utf-8

import abc

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget


# noinspection PyPep8Naming
class iTab(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent, flags=Qt.Widget)
        self.setContentsMargins(20, 20, 20, 20)

    @property
    @abc.abstractmethod
    def tab_title(self) -> str:
        """"""
