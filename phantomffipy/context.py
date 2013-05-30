from .library import acquire_library
try:
    import simplejson as json
except ImportError:
    import json


class Context(object):
    UNINITIALIZED = 0
    INITIALIZED = 1

    def __init__(self, ffi, library):
        self._context = None
        self.ffi = ffi
        self._library = library
        self.state = self.UNINITIALIZED
        self._config_proxy = None

    def __call__(self, methodname, *args, **kwargs):
        return getattr(self._library, methodname)(*args, **kwargs)

    def initialize(self):
        if self.state == self.UNINITIALIZED:
            self._context = self._library.ph_context_init()
            self._config_proxy = ContextConfig(self._library)
            self.state = self.INITIALIZED
        return self

    def destroy(self):
        if self.state & self.INITIALIZED:
            self._config_proxy = None
            self._library.ph_context_free(self._context)
            self.state = self.UNINITIALIZED
        return self

    def clear_memory_caches(self):
        if self.state & self.INITIALIZED:
            self._library.ph_context_clear_memory_cache()
            return self
        return None

    def set_object_cache_capacity(self, min_dead_capacity, max_dead,
                                  total_capacity):
        if self.state & self.INITIALIZED:
            self._library.ph_context_set_object_cache_capacity(
                min_dead_capacity, max_dead, total_capacity)
            return self
        return None

    def set_max_pages_in_cache(self, number_of_pages):
        if self.state & self.INITIALIZED:
            self._library.ph_context_set_max_pages_in_cache(number_of_pages)
            return self
        return None

    def get_all_cookies(self):
        cookies_json = None
        if self.state & self.INITIALIZED:
            cookies_json = self.ffi.string(
                self._library.ph_context_get_all_cookies())
            cookies_json = json.loads(cookies_json)
        return cookies_json

    @property
    def config(self):
        return self._config_proxy


class ContextConfig(object):
    SETTINGS = (None,
               ('LoadImages', bool,),
               ('Javascript', bool,),
               ('DnsPrefetching', bool,),
               ('Plugins', bool,),
               ('PrivateBrowsing', bool,),
               ('OfflineStorageDB', bool,),
               ('OfflineStorageQuota', int,),
               ('OfflineAppCache', bool,),
               ('FrameFlattening', bool,),
               ('LocalStorage', bool,),)

    def __init__(self, library):
        self._library = library


def set_prop(key, prop_type):
    def setter(self, new_val):
        if prop_type is bool:
            self._library.ph_context_set_boolean_config(key, int(new_val))
        elif prop_type is int:
            self._library.ph_context_set_int_config(key, int(new_val))
    return setter


def get_prop(key, prop_type):
    def getter(self):
        return prop_type(self._library.ph_context_get_boolean_config(key))
    return getter

for index, prop_and_type in enumerate(ContextConfig.SETTINGS):
    if prop_and_type:
        prop_name, prop_type = prop_and_type
        setattr(ContextConfig, prop_name.lower(),
                property(
                    get_prop(index, prop_type),
                    set_prop(index, prop_type)))


def acquire_context():
    '''
    Get a context from the pyphantom library.
    '''
    return Context(*acquire_library())
