from collections import OrderedDict


class PageDict(OrderedDict):
    def __init__(self, page, callback, *args, **kwargs):
        self.callback = callback
        self.page = page
        OrderedDict.__init__(self, *args, **kwargs)

    def update(self, iterable=None):
        '''TODO -- consider case of changing a setting while inited'''
        print "{0} os ".format(self.page._page)
        if self.callback:
            self.callback(self.page, list(iterable or self.itervalues()))
        if iterable:
            OrderedDict.update(self, iterable)


class PageSettings(object):
    def __init__(self, page):
        self.__page = page
        self.triggers = []
        self.__settings = {
            'geometry': PageDict(
                page,
                lambda page_instance, args: page_instance._context(
                    'ph_page_set_viewpoint_size',
                    *([page_instance._page] + args)),
                width=800, height=600)
        }
        for key in self.__settings.iterkeys():
            setattr(self, key, self.__settings[key])
            if self.__settings[key].callback:
                self.triggers.append(key)

    def trigger(self):
        for key in self.triggers:
            self.__settings[key].update()
