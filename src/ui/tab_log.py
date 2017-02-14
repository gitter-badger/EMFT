# coding=utf-8

import logging
from src import global_

from PyQt5.QtWidgets import QPlainTextEdit

from src.cfg import Config
from src.sentry import SENTRY
from src.ui.base import VLayout, Combo, PushButton, HLayout
from src.ui.itab import iTab
from src.ui.main_ui_interface import I
from utils import create_new_paste


class TabLog(iTab, logging.Handler):
    @property
    def tab_title(self) -> str:
        return 'Log'

    def __init__(self, parent=None):
        iTab.__init__(self, parent=parent)
        logging.Handler.__init__(self)

        self.levels = {
            'NOTSET': dict(level=0, color='#808080'),
            'DEBUG': dict(level=10, color='#808080'),
            'INFO': dict(level=20, color='#000000'),
            'WARNING': dict(level=30, color='#FFFF00'),
            'ERROR': dict(level=40, color='#FF0000'),
            'CRITICAL': dict(level=50, color='#FF0000'),
        }

        self.records = []

        self.setLevel(logging.DEBUG)
        self.setFormatter(
            logging.Formatter(
                '%(asctime)s: %(levelname)s: %(module)s.%(funcName)s - %(message)s',
                '%H:%M:%S'
            )
        )

        self.combo = Combo(
            on_change=self.combo_changed,
            choices=[
                'DEBUG',
                'INFO',
                'WARNING',
                'ERROR'
            ]
        )

        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)

        self._min_lvl = self.levels[Config().log_level]['level']
        self.combo.set_index_from_text(Config().log_level)

        self.clear_btn = PushButton('Clear', self._clean)
        self.send_btn = PushButton('Send', self._send)

        self.setLayout(
            VLayout(
                [
                    HLayout(
                        [
                            (self.combo, dict(stretch=1)),
                            (self.clear_btn, dict(stretch=0)),
                            (self.send_btn, dict(stretch=0)),
                        ]
                    ),
                    self.log_text,
                ]
            )
        )

        logger = logging.getLogger('__main__')
        logger.addHandler(self)
        self._clean()

    def emit(self, record: logging.LogRecord):
        self.records.append(record)
        if record.levelno >= self._min_lvl:
            I.write_log(self.format(record), str(self.levels[record.levelname]['color']))

    def write(self, msg, color='#000000', bold=False):
        msg = '<font color="{}">{}</font>'.format(color, msg)
        if bold:
            msg = '<b>{}</b>'.format(msg)
        self.log_text.appendHtml(msg)

    def combo_changed(self, new_value):
        Config().log_level = new_value
        self._set_log_level(new_value)

    def _send(self):
        content = []
        for rec in self.records:
            assert isinstance(rec, logging.LogRecord)
            content.append(self.format(rec))
            # SENTRY.add_crumb(rec.msg, 'LOG:{}'.format(rec.module), rec.levelname)
        url = create_new_paste('\n'.join(content))
        if url:
            SENTRY.captureMessage('Logfile', extra={'log_url': url})
            self.write('Log file sent; thank you !')
        else:
            self.write('Could not send log file')

    def _clean(self):
        self.log_text.clear()
        self.log_text.appendHtml('<b>Running EMFT v{}</b>'.format(global_.APP_VERSION))

    def _set_log_level(self, log_level):
        self._clean()
        self._min_lvl = self.levels[log_level]['level']
        for rec in self.records:
            assert isinstance(rec, logging.LogRecord)
            if rec.levelno >= self._min_lvl:
                self.write(self.format(rec))
