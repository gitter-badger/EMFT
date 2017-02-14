# coding=utf-8
import tempfile
from collections import OrderedDict
from os import walk, remove, rmdir
from os.path import exists, join
from zipfile import ZipFile, BadZipFile, ZipInfo

from sltp import SLTP
from utils import make_logger, Path

from src.global_ import ENCODING
from src.miz.mission import Mission

logger = make_logger('miz')


class Miz:
    def __init__(self, path_to_miz_file, temp_dir=None):

        path_to_miz_file = Path(path_to_miz_file).abspath()

        if not path_to_miz_file.exists():
            logger.error('miz file does not exist: {}'.format(path_to_miz_file))
            raise FileNotFoundError(path_to_miz_file)

        self.__src_miz_path = path_to_miz_file

        self.temp_dir_path = tempfile.mkdtemp(prefix='EMFT_') if temp_dir is None else temp_dir
        logger.debug('temporary directory for this mission object: {}'.format(self.temp_dir_path))

        self.files_in_zip = []

        self.__unzipped = False

        self.__l10n = OrderedDict()
        self.__mission = Mission(OrderedDict(), self.__l10n)

    def __enter__(self):
        logger.debug('instantiating new Mission object as a context')
        self.unzip()
        self.decode()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error('there were error with this mission, keeping temp dir at "{}" and re-raising'.format(
                self.temp_dir_path))
            logger.error(exc_type, exc_val)
            return False
        else:
            logger.debug('closing Mission object context')
            self.remove_temp_dir()

    @property
    def is_unzipped(self) -> bool:
        return self.__unzipped

    @property
    def src_miz_path(self) -> str:
        return self.__src_miz_path

    @property
    def l10n(self):
        return self.__l10n

    @property
    def mission(self):
        return self.__mission

    @property
    def mission_file_path(self) -> str:
        return Path(self.temp_dir_path).joinpath('mission').abspath()

    @property
    def ln10_file_path(self) -> str:
        return Path(self.temp_dir_path).joinpath('l10n', 'DEFAULT', 'dictionary').abspath()

    @property
    def default_destination(self) -> str:
        src = Path(self.src_miz_path)
        return src.dirname().joinpath(src.namebase + '_EMFT.miz').abspath()

    def decode_mission(self, ln10):

        if not self.is_unzipped:
            self.unzip()

        parser = SLTP()

        try:
            logger.debug('parsing mission lua table into dictionary')
            with open(self.mission_file_path, encoding=ENCODING) as _f:
                self.__mission = Mission(parser.decode('\n'.join(_f.readlines()[1:])), ln10)
        except:
            logger.exception('error while parsing mission lua table')
            raise

    def decode_ln10(self):

        if not self.is_unzipped:
            self.unzip()

        parser = SLTP()

        try:
            logger.debug('reading ln10 dictionary at: {}'.format(self.ln10_file_path))
            with open(self.ln10_file_path) as _f:
                self.__l10n = parser.decode('\n'.join(_f.readlines()[1:]))
        except:
            logger.exception('error while reading ln10 dictionary')
            raise

    def decode(self):
        logger.debug('reading Mission files from disk')
        self.decode_ln10()
        self.decode_mission(self.l10n)

    def unzip(self):
        """Extracts MIZ file into temp dir"""
        logger.debug('unzipping miz into temp dir: "{}" -> {}'.format(self.__src_miz_path, self.temp_dir_path))
        with ZipFile(self.__src_miz_path) as zip_file:
            try:
                logger.debug('reading infolist')
                zip_content = zip_file.infolist()
                self.files_in_zip = [f.filename for f in zip_content]
                for item in zip_content:  # not using ZipFile.extractall() for security reasons
                    assert isinstance(item, ZipInfo)
                    logger.debug('unzipping item: {}'.format(item.filename))
                    zip_file.extract(item, self.temp_dir_path)
            except BadZipFile:
                raise BadZipFile(self.__src_miz_path)
            except:
                logger.exception('error while unzipping miz file: {}'.format(self.__src_miz_path))
                raise
        logger.debug('checking miz content')
        for miz_item in map(join, [self.temp_dir_path],
                            ['./mission', './options', './warehouses', './l10n/DEFAULT/dictionary',
                             './l10n/DEFAULT/mapResource']):
            if not exists(miz_item):
                logger.error('missing file in miz: {}'.format(miz_item))
                raise FileNotFoundError(miz_item)
        logger.debug('all files have been found, miz successfully unzipped')
        self.__unzipped = True

    def _encode_mission(self):
        logger.debug('writing mission dictionary to mission file: {}'.format(self.mission_file_path))
        parser = SLTP()
        try:
            logger.debug('encoding dictionary to lua table')
            raw_text = parser.encode(self.__mission.d)
        except:
            logger.exception('error while encoding')
            raise
        try:
            logger.debug('overwriting mission file')
            with open(self.mission_file_path, mode="w", encoding=ENCODING, newline='') as _f:
                _f.write('mission = ')
                # raw_text = re_sub(RE_SPACE_AFTER_EQUAL_SIGN, "= \n", raw_text)
                _f.write(raw_text)
        except:
            logger.exception('error while writing mission file: {}'.format(self.mission_file_path))
            raise

    def _encode_ln10(self):
        logger.debug('writing ln10 to: {}'.format(self.ln10_file_path))
        parser = SLTP()
        try:
            logger.debug('encoding dictionary to lua table')
            raw_text = parser.encode(self.l10n)
        except:
            logger.exception('error while encoding')
            raise
        try:
            logger.debug('overwriting mission file')
            with open(self.ln10_file_path, mode="w", encoding=ENCODING, newline='') as _f:
                _f.write('dictionary = ')
                # raw_text = re_sub(RE_SPACE_AFTER_EQUAL_SIGN, "= \n", raw_text)
                _f.write(raw_text)
        except:
            logger.exception('error while writing ln10 file: {}'.format(self.ln10_file_path))
            raise

    def zip(self, destination=None):

        if destination is None:
            destination = self.default_destination
        else:
            destination = Path(destination).abspath()

        self._encode_mission()
        self._encode_ln10()

        try:
            logger.debug('zipping mission into: {}'.format(destination))
            print(destination)
            with ZipFile(destination, mode='w', compression=8) as _z:
                for f in self.files_in_zip:
                    # f = Path(self.temp_dir_path).joinpath(f)

                    abs_path = Path(self.temp_dir_path).joinpath(f).abspath()
                    logger.debug('injecting in zip file: {}'.format(abs_path))
                    _z.write(abs_path, arcname=f)

        except:
            logger.exception('error while zipping miz file')
            raise

        return True

    def remove_temp_dir(self):
        """Deletes the temporary directory"""
        logger.debug('removing temporary directory: {}'.format(self.temp_dir_path))
        files = []
        folders = []
        for root, _folders, _files in walk(self.temp_dir_path, topdown=False):
            for f in _folders:
                folders.append(join(root, f))
            for f in _files:
                files.append(join(root, f))
        for f in files:
            logger.debug('removing: {}'.format(f))
            try:
                remove(f)
            except:
                logger.exception('could not remove: {}'.format(f))
                raise
        for f in folders:
            logger.debug('removing: {}'.format(f))
            try:
                rmdir(f)
            except:
                logger.exception('could not remove: {}'.format(f))
                raise
        try:
            rmdir(self.temp_dir_path)
        except FileNotFoundError:
            pass
        except:
            logger.exception('could not remove: {}'.format(self.temp_dir_path))
            raise
