class GlobalManager(object):
    """
    全局单例管理器
    作用：在程序运行期间，跨模块/跨函数共享少量全局变量
    用法：
        gm = GlobalManager()
        gm.set_value("token", "abc123")
        print(gm.get_value("token"))
    """

    # 存储所有全局变量的字典（类变量，所有实例共享）
    _global_dict = {}
    # 单例实例引用（类变量，确保只生成一个对象）
    _instance = None

    def set_value(self, key, value):
        """
        设置全局变量
        :param key: 变量名，建议统一使用大写字符串，避免重复
        :param value: 任意类型，需要存储的值
        """
        self._global_dict[key] = value

    def get_value(self, key):
        """
        读取全局变量
        :param key: 变量名
        :return: 对应值；若 key 不存在，打印提示并返回 None
        """
        try:
            return self._global_dict[key]
        except KeyError:
            print(f"{key} 变量不存在")
            return None

    def __new__(cls, *args, **kwargs):
        """
        单例实现：第一次创建时把实例缓存到 cls._instance，
        后续再调用 GlobalManager() 直接返回缓存对象，保证全局唯一
        """
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance