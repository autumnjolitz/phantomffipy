from . import context as Context
from image import Image
from settings import PageSettings

FAILED_TO_LOAD_PAGE = "Failed to load page, url: {0}"


class Page(object):
    PAGE_UNLOADED = 0
    PAGE_CREATED = 1
    PAGE_LOAD_COMPLETE = 2

    def __init__(self, context=None):
        self._context = context or Context.acquire_context()
        self.state = self.PAGE_UNLOADED
        self.settings = PageSettings(self)
        self._url = None

    @property
    def url(self):
        return self._url

    @property
    def geometry(self):
        return self.settings.geometry

    @geometry.setter
    def geometry(self, iterable_geom):
        self.settings.geometry.update(iterable_geom)

    @property
    def source(self):
        if self.state & self.PAGE_LOAD_COMPLETE:
            return self._context.ffi.string(
                self._context('ph_frame_to_html', self._main_frame))
        return None

    def evaluate(self, javascript):
        if self.state & self.PAGE_LOAD_COMPLETE:
            if isinstance(javascript, unicode):
                javascript = javascript.encode('utf-8')
            return self._context.ffi.string(self._context(
                'ph_frame_evaluate_javascript', self._main_frame, javascript))
        return None

    def render(self, format=None, quality=-1):
        if self.state & self.PAGE_LOAD_COMPLETE:
            if not format:
                format = 'PNG'
            if isinstance(format, unicode):
                format = format.encode('utf-8')
            return Image(
                self._context('ph_frame_capture_image',
                              self._main_frame, format, quality),
                self._context)
        return None

    def open(self, url):
        if isinstance(url, unicode):
            url = url.encode('utf-8')  # unicode -> bytes
        if self._context.state == Context.Context.UNINITIALIZED:
            self._context.initialize()

        if self.state == self.PAGE_UNLOADED:
            self._page = self._context('ph_page_create')
            self.settings.trigger()
            self.state = self.PAGE_CREATED
        if self.state & self.PAGE_CREATED and \
                not self.state & self.PAGE_LOAD_COMPLETE:
            self._url = url
            if self._context('ph_page_load', self._page, self._url) != 0:
                self._close()
                raise RuntimeError(FAILED_TO_LOAD_PAGE.format(self._url))

            self._main_frame = self._context('ph_page_main_frame', self._page)
            self.state |= self.PAGE_LOAD_COMPLETE

    def close(self):
        self._context('ph_page_free', self._main_frame)
        self._context('ph_page_free', self._page)
        self._page = None
        self._main_frame = None
        self.state = self.PAGE_UNLOADED
