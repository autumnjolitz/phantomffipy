import os.path


class Image(object):
    def __init__(self, image_pointer, context):
        self._image_pointer = image_pointer
        self._context = context
        self._blob = None

    @property
    def blob(self):
        if not self._blob:
            size = self._context('ph_image_get_size', self._image_pointer)
            buf = self._context.ffi.new('char (*)[{0}]'.format(size))
            self._context(
                'ph_image_get_bytes', self._image_pointer, buf,
                size)
            self._context('ph_image_free', self._image_pointer)
            self._image_pointer = None
            self._blob = ''
            for index in xrange(0, size):
                self._blob += buf[0][index]

        return self._blob

    def save(self, path):
        if os.path.isdir(os.path.dirname(os.path.abspath(path))):
            with open(path, 'wb') as fh:
                fh.write(self.blob)

    def __repr__(self):
        return "{0}()".format(self.__class__.__name__)
