class GlobalManager(object):
    _global_dict = {}

    def set_value(self, key, value):
        self._global_dict[key] = value

    def get_value(self, key):
        try:
            return self._global_dict[key]
        except KeyError as e:
            print("获取的变量不存在：{}".format(key))

    def __new__(cls, *args, **kwargs):
        if cls._instance ==False:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
