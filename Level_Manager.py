from Init_Settings import *
from CS import *
from Util import FileUtils
from Logger import get_logger
logger = get_logger(__name__)
from Settings_Manager import Settings_Manager
sm = Settings_Manager()

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from UI import UI

from ttkbootstrap.dialogs.dialogs import Messagebox
import ttkbootstrap as tb
import os, shutil

class Level_Manager:
    def __init__(self, root: 'UI') -> None:
        self.root = root
        self.status_var: tb.StringVar = root.status_var
        self.progress: tb.Progressbar = root.progress

        self.zip_folder = sm.settings["zip_folder"]
        self.cache_folder = sm.settings["unzip_cache_folder"]

        self.level_list: list[Level] = []

    def load_levels(self) -> list[Level]:
        """
        加载所有关卡
        :return: 包含所有关卡的列表
        """
        # 处理压缩包
        self.process_archives()

        # 扫描关卡
        self.scan_levels()

        # 更新UI
        self.root.after(0, lambda: self.root._refresh_status_bar())
        if not self.level_list:
            self.status_var.set("没有发现任何关卡")
            self.root.after(0, lambda: Messagebox.show_info("没有发现任何关卡", "提示"))
        return self.level_list

    def process_archives(self) -> None:
        """
        处理压缩包
        """
        """处理压缩包文件"""
        archive_exts = ['.zip', '.rar', '.7z']
        archive_files = [
            f for f in os.listdir(self.zip_folder)
            if os.path.isfile(os.path.join(self.zip_folder, f)) and 
            any(f.lower().endswith(ext) for ext in archive_exts)
        ]
        
        if not archive_files:
            logger.info("没有需要处理的压缩包文件")
            self.root.after(0, lambda: self.status_var.set("没有需要处理的压缩包文件"))
            return
        
        logger.info(f"发现 {len(archive_files)} 个压缩包文件")
        self.root.after(0, lambda: self.status_var.set("正在处理压缩包..."))
        self.progress['maximum'] = len(archive_files)
        self.progress['value'] = 0
        
        for file in archive_files:
            file_path = os.path.join(self.zip_folder, file)
            try:
                base_name = os.path.splitext(file)[0]
                output_dir = os.path.join(self.cache_folder, base_name)
                
                # 检查是否已存在.adofai文件
                adofai_exists = False
                if os.path.exists(output_dir):
                    for f in os.listdir(output_dir):
                        if f.lower().endswith('.adofai'):
                            adofai_exists = True
                            break
                
                if adofai_exists:
                    logger.info(f"跳过已处理文件: {file}")
                    self.root.after(0, lambda: self.status_var.set(f"跳过已处理文件: {file}"))
                    self.progress['value'] += 1
                    continue
                
                # 创建目录
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # 复制原始压缩包
                shutil.copy2(file_path, output_dir)
                
                # 解压.adofai文件
                FileUtils.extract_adofai_only(file_path, output_dir)
                
                logger.info(f"成功处理: {file} 到 {output_dir}")
                self.root.after(0, lambda: self.status_var.set(f"成功处理: {file} 到 {output_dir}"))
                self.progress['value'] += 1
            except Exception as e:
                logger.error(f"处理失败 {file}: {e}")
                self.root.after(0, lambda e=e: self.status_var.set(f"处理失败 {file}: {e}"))
                self.progress['value'] += 1

    def scan_levels(self) -> None:
        """
        扫描关卡文件夹
        """
        # 扫描所有子目录
        level_folders: list[str] = []
        for root_dir, subdirs, _ in os.walk(self.cache_folder):
            if root_dir != self.cache_folder:
                level_folders.append(root_dir)
        
        if not level_folders:
            logger.info("在缓存路径下未找到任何关卡文件夹")
            self.root.after(0, lambda: self.status_var.set("在缓存路径下未找到任何关卡文件夹"))
            return
        
        logger.info(f"发现 {len(level_folders)} 个关卡文件夹")
        self.root.after(0, lambda: self.status_var.set(f"发现 {len(level_folders)} 个关卡文件夹"))
        self.progress['maximum'] = len(level_folders)
        self.progress['value'] = 0

        for folder_path in level_folders:
            adofai_files = [
                f for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(".adofai")
            ]
            
            if not adofai_files:
                self.progress['value'] += 1
                continue
            
            file_path = os.path.join(folder_path, adofai_files[0])
            try:
                level = Level(file_path)
                self.level_list.append(level)
                logger.info(f"成功加载关卡: {file_path}")
                self.root.after(0, lambda: self.status_var.set(f"成功加载关卡: {file_path}"))
            except Exception as e:
                logger.error(f"加载关卡失败 {file_path}: {e}")
                self.root.after(0, lambda e=e: self.status_var.set(f"加载关卡失败 {file_path}: {e}"))
            finally:
                self.progress['value'] += 1
            






