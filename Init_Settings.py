# 配置文件
VERSION = "1.0.0"
SETTINGS_FILE = f"tl_settings_{VERSION}.json"
THEMENAME = "darkly"
SSLC = 3  # 单次滚轮滚动单位

LOAD_THREAD: int = 20  # 加载关卡的线程数

DEFAULT_SETTINGS = {
    "zip_folder": "",
    "save_folder": "",
    "unzip_cache_folder": "",
    'auto_load': False,
    'types': [
        "Init"
    ]
}
