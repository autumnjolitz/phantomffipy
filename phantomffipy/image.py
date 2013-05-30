import os.path


class Image(object):
    def __init__(self, image_pointer, context):
        self._image_pointer = image_pointer
        self._context = context
        self._blob = None

    @property
    def blob(self):
        if not self._blob:
            self.blob = self._context(
                'ph_image_get_bytes', self._image_pointer,
                self._context('ph_image_get_size', self._image_pointer))
            self._context('ph_image_free', self._image_pointer)
            self._image_pointer = None
        return self._blob

    def save(self, path):
        if os.path.isdir(os.path.dirname(os.path.abspath(path))):
            with open(path, 'wb') as fh:
                fh.write(self.blob)

    def __repr__(self):
        return "{0}()".format(self.__class__.__name__)
