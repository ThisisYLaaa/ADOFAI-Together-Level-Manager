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
from concurrent.futures import ThreadPoolExecutor, wait
import threading

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

    def _process_single_archive(self, file: str, progress_lock: threading.Lock) -> None:
        """
        处理单个压缩包文件(线程安全)
        :param file: 压缩包文件名
        :param progress_lock: 进度更新锁
        """
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
            else:
                # 创建目录
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # 复制原始压缩包
                shutil.copy2(file_path, output_dir)
                
                # 解压.adofai文件
                FileUtils.extract_adofai_only(file_path, output_dir)
                
                logger.info(f"成功处理: {file} 到 {output_dir}")
                self.root.after(0, lambda: self.status_var.set(f"成功处理: {file} 到 {output_dir}"))
        except Exception as e:
            logger.error(f"处理失败 {file}: {e}")
            self.root.after(0, lambda e=e: self.status_var.set(f"处理失败 {file}: {e}"))
        finally:
            # 线程安全地更新进度
            with progress_lock:
                self.progress['value'] += 1

    def process_archives(self) -> None:
        """
        处理压缩包
        """
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
        
        # 创建进度更新锁
        progress_lock = threading.Lock()
        
        # 使用线程池处理压缩包
        with ThreadPoolExecutor(max_workers=LOAD_THREAD) as executor:
            # 提交所有任务
            futures = [
                executor.submit(self._process_single_archive, file, progress_lock)
                for file in archive_files
            ]
            # 等待所有任务完成
            wait(futures)

    def _scan_single_folder(self, folder_path: str, progress_lock: threading.Lock, level_lock: threading.Lock) -> None:
        """
        扫描单个关卡文件夹(线程安全)
        :param folder_path: 文件夹路径
        :param progress_lock: 进度更新锁
        :param level_lock: 关卡列表更新锁
        """
        try:
            adofai_files = [
                f for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(".adofai")
            ]
            
            if not adofai_files:
                return
            
            file_path = os.path.join(folder_path, adofai_files[0])
            try:
                level = Level(file_path)
                # 线程安全地添加到关卡列表
                with level_lock:
                    self.level_list.append(level)
                logger.info(f"成功加载关卡: {file_path}")
                self.root.after(0, lambda: self.status_var.set(f"成功加载关卡: {file_path}"))
            except Exception as e:
                logger.error(f"加载关卡失败 {file_path}: {e}")
                self.root.after(0, lambda e=e: self.status_var.set(f"加载关卡失败 {file_path}: {e}"))
        finally:
            # 线程安全地更新进度
            with progress_lock:
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

        # 创建锁
        progress_lock = threading.Lock()
        level_lock = threading.Lock()
        
        # 使用线程池扫描关卡文件夹
        with ThreadPoolExecutor(max_workers=LOAD_THREAD) as executor:
            # 提交所有任务
            futures = [
                executor.submit(self._scan_single_folder, folder_path, progress_lock, level_lock)
                for folder_path in level_folders
            ]
            # 等待所有任务完成
            wait(futures)
