# coding=utf-8

# noinspection PyProtectedMember
from abc import abstractmethod
from utils import Singleton


class ProgressAdapter:

    @staticmethod
    @abstractmethod
    def progress_start(title: str, length: int = 100, label: str = ''):
        """"""

    @staticmethod
    @abstractmethod
    def progress_set_value(value: int):
        """"""

    @staticmethod
    @abstractmethod
    def progress_set_label(value: str):
        """"""

    @staticmethod
    @abstractmethod
    def progress_done():
        """"""


class Progress:

    def __init__(self):
        raise RuntimeError('do NOT instantiate')

    adapters = []
    title = None
    label = None
    value = 0
    length = 100
    started = False

    @staticmethod
    def _check_adapter(adapter):
        if not issubclass(adapter, ProgressAdapter):
            raise TypeError(adapter.__class__)

    @staticmethod
    def has_adapter(adapter: ProgressAdapter):
        return adapter in Progress.adapters

    @staticmethod
    def register_adapter(adapter: ProgressAdapter):
        Progress._check_adapter(adapter)
        if Progress.has_adapter(adapter):
            return
        Progress.adapters.append(adapter)

    @staticmethod
    def unregister_adapter(adapter: ProgressAdapter or str):
        if Progress.has_adapter(adapter):
            Progress.adapters.remove(adapter)

    @staticmethod
    def start(title: str, length: int, label: str = ''):
        for adapter in Progress.adapters:
            adapter.progress_start(title, length, label)

    @staticmethod
    def set_value(value):
        for adapter in Progress.adapters:
            adapter.progress_set_value(value)

    @staticmethod
    def set_label(value):
        for adapter in Progress.adapters:
            adapter.progress_set_label(value)

    @staticmethod
    def done():
        for adapter in Progress.adapters:
            adapter.progress_done()