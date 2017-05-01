# coding=utf-8

import logging

from utils import create_new_paste

from src import global_
from src.cfg import Config
from src.misc.logging_handler import PersistentLoggingFollower
from src.sentry import SENTRY
from src.ui.base import PlainTextEdit
from src.ui.base import VLayout, Combo, PushButton, HLayout, LineEdit, Label, GridLayout
from src.ui.itab import iTab
from src.ui.main_ui_interface import I


class TabLog(iTab, PersistentLoggingFollower):
    @property
    def datefmt_(self):
        return '%H:%M:%S'

    @property
    def fmt_(self):
        return '%(asctime)s: [%(levelname)8s]: (%(threadName)-9s) - %(name)s - %(funcName)s - %(message)s'
        # return '%(asctime)s: %(levelname)8s: [%(threadName)-9s]: %(module)s.%(funcName)s - %(message)s'

    @property
    def tab_title(self) -> str:
        return 'Log'

    def __init__(self, parent=None):
        PersistentLoggingFollower.__init__(self)
        iTab.__init__(self, parent=parent)

        self.colors = {
            'NOTSET': '#808080',
            'DEBUG': '#808080',
            'INFO': '#000000',
            'WARNING': '#FF5500',
            'ERROR': '#FF0000',
            'CRITICAL': '#FF0000',
        }

        self.combo = Combo(
            on_change=self.combo_changed,
            choices=[
                'DEBUG',
                'INFO',
                'WARNING',
                'ERROR'
            ]
        )

        self.filter_line_edit_msg = LineEdit('', self._filter_updated, clear_btn_enabled=True)
        self.filter_line_edit_module = LineEdit('', self._filter_updated, clear_btn_enabled=True)
        self.filter_line_edit_thread = LineEdit('', self._filter_updated, clear_btn_enabled=True)

        self.log_text = PlainTextEdit(read_only=True)
        self.combo.set_index_from_text(Config().log_level)

        self.clear_btn = PushButton('Clear log', self._clean)
        self.send_btn = PushButton('Send log', self._send)

        self.setLayout(
            VLayout(
                [
                    HLayout(
                        [
                            (self.combo, dict(stretch=1)),
                            20,
                            (self.clear_btn, dict(stretch=0)),
                            (self.send_btn, dict(stretch=0)),
                        ]
                    ),
                    GridLayout(
                        [
                            [Label('Filter message'), self.filter_line_edit_msg],
                            [Label('Filter module'), self.filter_line_edit_module],
                            [Label('Filter thread'), self.filter_line_edit_thread],
                        ]
                    ),
                    self.log_text,
                ]
            )
        )

        # logger = logging.getLogger('__main__')
        # logger.addHandler(self)
        self._filter_updated()

    @property
    def min_lvl(self):
        return self.combo.currentText()

    def _filter_updated(self):
        self._clean()
        self.filter_records(
            minimum_level=self.min_lvl,
            msg_filter=self.filter_line_edit_msg.text(),
            module_filter=self.filter_line_edit_module.text(),
            thread_filter=self.filter_line_edit_thread.text(),
        )

    def handle_record(self, record: logging.LogRecord):
        if record.levelno >= self._sanitize_level(self.min_lvl):
            I.write_log(self.format(record), str(self.colors[record.levelname]))

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
        for rec in self.filter_records():
            assert isinstance(rec, logging.LogRecord)
            content.append(self.format(rec))
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
        self.filter_records(
            minimum_level=log_level
        )
