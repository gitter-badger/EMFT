# coding=utf-8
from queue import Queue
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QShortcut

# noinspection PyProtectedMember
from src import _global
from .base import Shortcut, VLayout, Widget
from .itab import iTab
from .main_ui_progress import MainUiProgress, MainUIProgressAdapter
from .main_ui_threading import MainGuiThreading
from .main_ui_interface import I
from utils import Updater, make_logger, Progress

logger = make_logger(__name__)


class MainUi(QMainWindow, MainGuiThreading, MainUiProgress):

    threading_queue = Queue()

    def __init__(self):
        # Fucking QMainWindow calls a general super().__init__ on every parent class, don't call them here !
        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint
        flags = flags | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint

        QMainWindow.__init__(
            self,
            parent=None,
            flags=flags
        )

        self.resize(1024, 768)

        self.tabs = QTabWidget()

        layout = VLayout(
            [
                self.tabs
            ]
        )

        layout.setContentsMargins(10, 10, 10, 10)

        window = Widget()
        window.setLayout(layout)

        self.setCentralWidget(window)

        self.setWindowIcon(QIcon(':/ico/app.ico'))

        self.exit_shortcut = Shortcut(QKeySequence(Qt.Key_Escape), self, self.exit)

    def show_log_tab(self):
        self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def add_tab(self, tab: iTab):
        self.tabs.addTab(tab, tab.tab_title)

    def show(self):
        self.setWindowTitle(
            '{} v{} - {}'.format(_global.APP_SHORT_NAME,
                                 _global.APP_VERSION,
                                 _global.APP_RELEASE_NAME))
        self.setWindowState(self.windowState() & Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
        super(QMainWindow, self).show()

        self.raise_()

    @staticmethod
    def exit(code=0):
        if _global.QT_APP:
            _global.QT_APP.exit(code)

    def closeEvent(self, event):
        self.exit()


def start_ui():
    from PyQt5.QtWidgets import QApplication
    import sys
    from src.ui.tab_reorder import TabReorder
    from src.ui.tab_log import TabLog
    logger.debug('starting QtApp object')
    _global.QT_APP = QApplication([])
    _global.MAIN_UI = MainUi()
    _global.MAIN_UI.add_tab(TabReorder())
    _global.MAIN_UI.add_tab(TabLog())
    _global.MAIN_UI.show()

    # from utils.threadpool import ThreadPool
    # update_thread = ThreadPool(1, 'updater', True)
    # update_thread.queue_task()
    # updater = Updater(
    #     executable_name='EMFT.exe',
    #     current_version=_global.APP_VERSION,
    #     gh_user='132nd-etcher',
    #     gh_repo='test',
    #     asset_filename='EMFT.exe',
    #     pre_update_func=I.hide,
    #     cancel_update_func=I.show)
    # updater.version_check('alpha')

    # Progress().register_adapter(MainUIProgressAdapter())

    sys.exit(_global.QT_APP.exec())
