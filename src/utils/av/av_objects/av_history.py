# coding=utf-8

from src.utils.custom_session import JSONObject
from .av_build import AVAllBuilds
from .av_project import AVProject


class AVHistory(JSONObject):
    @property
    def project(self):
        return AVProject(self.json['project'])

    @property
    def builds(self):
        return AVAllBuilds(self.json['builds'])
