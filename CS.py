# 自定义类
from Parser import Parser
from Util import *

import os, time

class Level:
    def __init__(self, file_path):
        self.dir_path: str = os.path.dirname(file_path)
        self.file_path: str = file_path
        self.data: dict = Parser(file_path)()

        self.song: str = self.data['settings']['song']
        self.artist: str = self.data['settings']['artist']
        self.author: str = self.data['settings']['author']
        
        # 没有指定日期时，尝试从压缩包中提取
        archive_path: str = ""
        for f in os.listdir(self.dir_path):
            if f.lower().endswith(('.zip', '.rar', '.7z')):
                archive_path = os.path.join(self.dir_path, f)
                mtime = os.path.getmtime(archive_path)
                self.date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
                break
        
        # 没有指定歌曲名时，尝试从文件夹中提取
        if not self.song:
            audio_files = [f for f in os.listdir(self.dir_path) if f.lower().endswith(('.ogg', '.wav'))]
            if audio_files:
                self.song = str([os.path.splitext(f)[0] for f in audio_files]) if len(audio_files) > 1 else os.path.splitext(audio_files[0])[0]
        self.song = HtmlUtils.clean_html_tags(self.song) or 'unknown'
        self.artist = HtmlUtils.clean_html_tags(self.artist) or 'unknown'
        self.author = HtmlUtils.clean_html_tags(self.author) or 'unknown'
        self.date = self.date or 'unknown'
        
        self.size: int = len(self.data["angleData"])
        self.archive_path: str = archive_path
    
    def get_display_values(self) -> tuple:
        """
        返回树形视图中显示的四列值
        :return: 包含四列值的元组 (歌曲名, 艺术家, 作者, 日期)
        """
        return self.song, self.artist, self.author, self.date

    def save(self, save_path: str) -> bool:
        """
        保存当前关卡数据到指定路径
        :param save_path: 保存路径
        :return: 是否成功保存
        """
        try:
            folder_name: str = f"{self.song}_{self.artist}_{self.author}"
            folder_name = FileUtils.sanitize_filename(folder_name)
            save_folder: str = os.path.join(save_path, folder_name)
            os.makedirs(save_folder, exist_ok=True)
            FileUtils.extract_full_archive(self.archive_path, save_folder)
            return True
        except Exception as e:
            logger.error(f"保存关卡失败: {e}")
            return False
