# 工具 不要使用try except
from Logger import get_logger
logger = get_logger(__name__)
import os, re, subprocess, html, shutil

class FileUtils:
    """文件操作工具类"""
    @staticmethod
    def get_7z_path():
        """获取Together安装目录中的7z路径"""
        appdata = os.getenv('LOCALAPPDATA')
        if not appdata:
            return None
        
        together_path = os.path.join(appdata, "Together", "Resources", "7z", "7z.exe")
        if os.path.exists(together_path):
            return together_path
        return None

    @staticmethod
    def sanitize_filename(name):
        """移除文件名中的非法字符"""
        if not name:
            return "未知关卡"
        return re.sub(r'[<>:"/\\|?*]', '', name).strip()

    @staticmethod
    def extract_full_archive(archive_path, output_dir):
        """解压完整压缩包"""
        seven_zip_path = FileUtils.get_7z_path()
        if not seven_zip_path:
            logger.error("未找到Together自带的7z.exe")
            raise Exception("未找到Together自带的7z.exe")
        
        os.makedirs(output_dir, exist_ok=True)
        
        command = [
            seven_zip_path,
            'x',  # 完整解压
            f'-o{output_dir}',
            '-y',  # 覆盖所有文件
            archive_path
        ]
        
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('gbk', errors='ignore') if e.stderr else str(e)
            logger.error(f"解压错误: {error_msg}")
            raise Exception(f"解压失败: {archive_path}")

    @staticmethod
    def extract_adofai_only(archive_path, output_dir):
        """只解压.adofai文件"""
        seven_zip_path = FileUtils.get_7z_path()
        if not seven_zip_path:
            logger.error("未找到Together自带的7z.exe")
            raise Exception("未找到Together自带的7z.exe")
        
        command = [
            seven_zip_path,
            'e',  # 只解压文件，不保留目录结构
            f'-o{output_dir}',
            '-y',  # 覆盖所有文件
            archive_path,
            '-r',  # 递归查找所有子目录
            '*.adofai',
            '*.ogg',
            '*.wav'
        ]
        
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                check=True
            )
            logger.info(f"解压成功: {archive_path} 到 {output_dir}")
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('gbk', errors='ignore') if e.stderr else str(e)
            logger.error(f"解压错误: {error_msg}")
            raise Exception(f"解压失败: {archive_path}")

    @staticmethod
    def clear_directory(directory):
        """清空目录下所有文件"""
        if not os.path.exists(directory):
            return
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
                logger.info(f"删除文件: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                logger.info(f"删除目录: {item_path}")

class HtmlUtils:
    """HTML处理工具类"""
    @staticmethod
    def clean_html_tags(text):
        if not isinstance(text, str):
            return text
        
        text = html.unescape(text)
        text = re.sub(r'<color=[^>]*>', '', text)
        text = re.sub(r'<size=[^>]*>', '', text)
        text = re.sub(r'</?(color|size|b|i|u|br)[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()
