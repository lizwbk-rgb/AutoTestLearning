class GlobalManager(object):
    _global_dict = {}
    _instance = None

    def set_value(self, key, value):
        self._global_dict[key] = value

    def get_value(self, key):
        try:
            return self._global_dict[key]
        except KeyError as e:
            print("{}变量不存在".format(key))

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance



