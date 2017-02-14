# coding=utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QProgressDialog
from utils import ProgressAdapter

from src import _global


class MainUiProgress:
    """"""

    def __init__(self):
        self.progress = None

    def progress_start(self, title, length, label):
        self.progress = QProgressDialog()
        self.progress.setWindowFlags(Qt.FramelessWindowHint)
        self.progress.setWindowFlags(Qt.WindowTitleHint)
        self.progress.setMinimumWidth(400)
        from PyQt5.QtWidgets import QPushButton
        # QString() seems to be deprecated in v5
        # PyQt does not support setCancelButton(0) as it expects a QPushButton instance
        # Get your shit together, Qt !
        self.progress.findChild(QPushButton).hide()
        self.progress.setMinimumDuration(1)
        self.progress.setWindowModality(Qt.ApplicationModal)
        self.progress.setCancelButtonText('')
        self.progress.setWindowIcon(QIcon(':/ico/app.ico'))
        self.progress.setWindowTitle(title)
        self.progress.setLabelText(label)
        self.progress.setMaximum(length)
        self.progress.show()

    def progress_set_value(self, value: int):
        self.progress.setValue(value)

    def progress_set_label(self, value: str):
        self.progress.setLabelText(value)

    def progress_done(self):
        self.progress.setValue(self.progress.maximum())
        self.progress = None


class MainUIProgressAdapter(ProgressAdapter):
    @staticmethod
    def __progress_wrapper(func_name, *args, **kwargs):
        if _global.MAIN_UI:
            _global.MAIN_UI.do('main_ui', func_name, *args, **kwargs)

    @property
    def name(self) -> str:
        return 'MainUIProgress'

    @staticmethod
    def set_value(value: int):
        MainUIProgressAdapter.__progress_wrapper('set_value', value)

    @staticmethod
    def start(title: str, length: int = 100, label: str = ''):
        MainUIProgressAdapter.__progress_wrapper('progress_start', title, length, label)

    @staticmethod
    def set_label(value: str):
        MainUIProgressAdapter.__progress_wrapper('set_label', value)

    @staticmethod
    def done():
        MainUIProgressAdapter.__progress_wrapper('progress_done')