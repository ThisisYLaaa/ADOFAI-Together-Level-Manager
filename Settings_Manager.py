# 配置管理器
from Init_Settings import *

from Logger import get_logger
logger = get_logger(__name__)

import json, os

class Settings_Manager:
    _Settings_Manager_instance = None
    _Settings_Manager_initialized = False

    def __new__(cls):
        if cls._Settings_Manager_instance is None:
            cls._Settings_Manager_instance = super(Settings_Manager, cls).__new__(cls)
        return cls._Settings_Manager_instance
    
    def __init__(self) -> None:
        if Settings_Manager._Settings_Manager_initialized:
            return
        self.settings: dict = {}
        self.load_settings()
        Settings_Manager._Settings_Manager_initialized = True
    
    def load_settings(self) -> None:
        """加载设置"""
        logger.info("加载设置")
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
            # 添加缺失的设置项
            for key, default_value in DEFAULT_SETTINGS.items():
                if key not in self.settings:
                    self.settings[key] = default_value
            logger.info("设置加载成功")
            self.create_folder()
            return

        except FileNotFoundError:
            logger.error("设置文件未找到")
        except json.JSONDecodeError:
            logger.error("设置文件格式错误")
        except Exception as e:
            logger.error(f"加载设置时发生未知错误: {e}")
        self.settings = DEFAULT_SETTINGS.copy()
        logger.info("使用默认设置")
        self.save_settings()
    
    def save_settings(self) -> None:
        """保存设置"""
        logger.info("💾 保存设置")
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            logger.info("设置保存成功")
            self.create_folder()

        except PermissionError as e:
            logger.error(f"保存设置时权限错误: {e}")
        except IOError as e:
            logger.error(f"保存设置时IO错误: {e}")
        except Exception as e:
            logger.error(f"保存设置时发生未知错误: {e}")
    
    def change(self, key: str, value) -> None:
        """改变设置"""
        if key not in self.settings:
            logger.error(f"设置项 {key} 不存在")
            return
        self.settings[key] = value
    
    def create_folder(self) -> None:
        """创建必要的文件夹"""
        try:
            if self.settings["unzip_cache_folder"]:
                os.makedirs(self.settings["unzip_cache_folder"], exist_ok=True)
            if self.settings["save_folder"]:
                os.makedirs(self.settings["save_folder"], exist_ok=True)
        except Exception as e:
            logger.error(f"创建文件夹时发生未知错误: {e}")
