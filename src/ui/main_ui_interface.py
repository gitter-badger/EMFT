# coding=utf-8


from utils import ProgressAdapter

from src import global_


class MainUiMethod:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        if global_.MAIN_UI is None:
            raise RuntimeError('Main UI not initialized')
        global_.MAIN_UI.do('main_ui', self.func.__name__, *args, **kwargs)


class I(ProgressAdapter):
    @staticmethod
    @MainUiMethod
    def show_log_tab():
        """"""

    @staticmethod
    @MainUiMethod
    def show():
        """"""

    @staticmethod
    @MainUiMethod
    def write_log(value: str, color: str):
        """"""

    @staticmethod
    @MainUiMethod
    def hide():
        """"""

    @staticmethod
    @MainUiMethod
    def progress_set_value(value: int):
        """"""

    @staticmethod
    @MainUiMethod
    def progress_start(title: str, length: int = 100, label: str = ''):
        """"""

    @staticmethod
    @MainUiMethod
    def progress_set_label(value: str):
        """"""

    @staticmethod
    @MainUiMethod
    def progress_done():
        """"""
