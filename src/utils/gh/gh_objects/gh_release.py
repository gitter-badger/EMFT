# coding=utf-8

from src.utils.custom_session import JSONObject, json_property
from .gh_user import GHUser
from .gh_asset import GHAllAssets


class GHRelease(JSONObject):
    @json_property
    def url(self):
        """"""

    @json_property
    def html_url(self):
        """"""

    @json_property
    def assets_url(self):
        """"""

    @json_property
    def tag_name(self):
        """"""

    @json_property
    def name(self):
        """"""

    @json_property
    def draft(self):
        """"""

    @json_property
    def prerelease(self):
        """"""

    @json_property
    def created_at(self):
        """"""

    @json_property
    def published_at(self):
        """"""

    @json_property
    def body(self):
        """"""

    @property
    def author(self):
        return GHUser(self.json['author'])

    @property
    def assets(self):
        return GHAllAssets(self.json['assets'])

    @property
    def assets_count(self):
        return len(self.assets)


class GHAllReleases(JSONObject):
    def __iter__(self):
        for x in self.json:
            yield GHRelease(x)

    def final_only(self):
        for x in self:
            if not x.prerelease:
                yield x

    def prerelease_only(self):
        for x in self:
            if x.prerelease:
                yield x

    def __getitem__(self, item) -> GHRelease:
        for rel in self:
            if rel.name == item:
                return rel
        raise AttributeError('release not found: {}'.format(item))

    def __len__(self) -> int:
        return len(self.json)

    def __contains__(self, item) -> bool:
        try:
            self.__getitem__(item)
            return True
        except AttributeError:
            return False
