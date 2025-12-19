# 图形化界面
from Init_Settings import *
from CS import *
from TreeView import TreeViewHelper
from Level_Manager import Level_Manager
from Logger import get_logger
logger = get_logger(__name__)
from Settings_Manager import Settings_Manager
sm = Settings_Manager()

import ttkbootstrap as tb
from ttkbootstrap.dialogs.dialogs import Messagebox
from tkinter import filedialog
import threading

class Window_Settings(tb.Toplevel):
    def __init__(self, parent: tb.Window) -> None:
        super().__init__()
        self.title("设置")
        # self.geometry("800x400")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.autoload_var: tb.BooleanVar = tb.BooleanVar(value=sm.settings["auto_load"])
        self.zip_folder_var: tb.StringVar = tb.StringVar(value=sm.settings["zip_folder"])
        self.save_folder_var: tb.StringVar = tb.StringVar(value=sm.settings["save_folder"])
        self.unzip_cache_folder_var: tb.StringVar = tb.StringVar(value=sm.settings["unzip_cache_folder"])

        self.create_widgets()

    def on_close(self) -> None:
        self.destroy()
    
    def _browse_folder(self, entry: tb.Entry) -> None:
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, "end")
            entry.insert(0, folder)
        self.focus_set()

    def create_widgets(self) -> None:
        ent_list: list[tuple[str, str]] = [
            ("压缩包文件夹", "zip_folder"),
            ("保存路径", "save_folder"),
            ("缓存文件夹", "unzip_cache_folder"),
        ]
        
        f_ent = tb.Frame(self)
        f_ent.pack(fill="x", anchor="nw")
        for text, var in ent_list:
            lf = tb.Labelframe(f_ent, text=text)
            lf.pack(fill="x", padx=10, pady=10)
            ent = tb.Entry(
                lf,
                textvariable=getattr(self, f"{var}_var"),
                width=80
                )
            ent.pack(side="left", padx=10, pady=10)
            tb.Button(
                lf,
                text="浏览",
                command=lambda e=ent: self._browse_folder(e),
                bootstyle="primary"
            ).pack(side="left", padx=10)
        
        # 自动加载
        tb.Checkbutton(
            self,
            text="自动加载",
            bootstyle="primary",
            variable=self.autoload_var
        ).pack(anchor="nw", padx=10, pady=10)
        
        # 保存按钮
        f_btn = tb.Frame(self)
        f_btn.pack(fill="x", anchor="nw")
        tb.Button(
            f_btn,
            text="保存",
            command=self.save_settings,
            bootstyle="primary"
        ).pack(side="left", padx=10, pady=10)
        tb.Button(
            f_btn,
            text="取消",
            command=self.on_close,
            bootstyle="danger"
        ).pack(side="left", padx=10, pady=10)
    
    def save_settings(self) -> None:
        sm.change("auto_load", self.autoload_var.get())
        sm.change("zip_folder", self.zip_folder_var.get())
        sm.change("save_folder", self.save_folder_var.get())
        sm.change("unzip_cache_folder", self.unzip_cache_folder_var.get())
        sm.save_settings()
        self.on_close()

class Window_Types_Manager(tb.Toplevel):
    def __init__(self, parent: tb.Window) -> None:
        super().__init__()
        self.title("类型管理")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.create_widgets()

    def on_close(self) -> None:
        self.destroy()

    def create_widgets(self) -> None:
        self.types_text: tb.Text = tb.Text(self, width=40, height=20)
        self.types_text.pack(fill="x", padx=10, pady=5)
        self.types_text.insert("1.0", "\n".join(sm.settings["types"]))

        # 保存按钮
        f_btn = tb.Frame(self)
        f_btn.pack(fill="x", anchor="nw")
        tb.Button(
            f_btn,
            text="保存",
            command=self.save_types,
            bootstyle="primary"
        ).pack(side="left", padx=10, pady=5)
        tb.Button(
            f_btn,
            text="取消",
            command=self.on_close,
            bootstyle="danger"
        ).pack(side="left", padx=10, pady=5)
    
    def save_types(self) -> None:
        types = self.types_text.get("1.0", "end-1c").split("\n")
        sm.change("types", types)
        sm.save_settings()
        self.on_close()

class Window_Saving(tb.Toplevel):
    def __init__(self, parent: "UI") -> None:
        super().__init__()
        self.title("保存")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.geometry("400x200")
        self.parent: "UI" = parent

        # 从parent中获取tree被选中的item
        self.level_data: list[Level] = self.parent.level_data
        self.selected_items: tuple[str, ...] = self.parent.tree.selection()
        if not self.selected_items:
            logger.error("请先选择一个项目")
            self.parent.after(0, lambda: Messagebox.show_error("请先选择一个项目", "错误"))
            self.on_close()
            return
        
        self.save_folder: str = sm.settings["save_folder"]
        self.save_path_var: tb.StringVar = tb.StringVar()
        self.type_var: tb.StringVar = tb.StringVar(value=sm.settings["types"][0])
        self.types: list[str] = sm.settings["types"].copy()
        self.type_var.trace_add("write", self._update_save_path)
        self._update_save_path()

        self.create_widgets()
    
    def on_close(self) -> None:
        self.destroy()
    
    def _update_save_path(self, *args) -> None:
        save_path: str = os.path.join(
            self.save_folder,
            self.type_var.get()
        ).replace("/", "\\")
        self.save_path_var.set(save_path)
    
    def create_widgets(self) -> None:
        lf_type = tb.Labelframe(self, text="类型")
        lf_type.pack(fill="x", padx=10, pady=5)
        tb.Combobox(
            lf_type,
            textvariable=self.type_var,
            values=self.types,
            bootstyle="primary"
        ).pack(fill="x", padx=10, pady=5)
        l_save_path = tb.Label(lf_type, textvariable=self.save_path_var)
        l_save_path.pack(fill="x", padx=10, pady=5)

        f_btn = tb.Frame(self)
        f_btn.pack(fill="x", anchor="nw")
        tb.Button(
            f_btn,
            text="保存",
            command=self.save_levels,
            bootstyle="primary"
        ).pack(side="left", padx=10, pady=5)
        tb.Button(
            f_btn,
            text="取消",
            command=self.on_close,
            bootstyle="danger"
        ).pack(side="left", padx=10, pady=5)
    
    def save_levels(self) -> None:
        def th():
            success: int = 0
            self.parent.progress["value"] = 0
            for item in self.selected_items:
                # 通过项目ID直接获取对应的Level对象
                level: Level = self.parent.tree.level_map[item]
                if level.save(self.save_path_var.get()):
                    success += 1
                self.parent.status_var.set(f"保存 {success}/{len(self.selected_items)} 个关卡")
                self.parent.progress["value"] = (success / len(self.selected_items)) * 100
        
        thread = threading.Thread(target=th)
        thread.start()
        self.on_close()

class UI(tb.Window):
    def __init__(self) -> None:
        super().__init__(themename=THEMENAME)
        self.title(f"Together Level Manager v{VERSION}")
        self.geometry("1000x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.settings_window: Window_Settings | None = None

        self.level_data: list[Level] = []
        self.status_var: tb.StringVar = tb.StringVar()
        self._refresh_status_bar()

        self.create_widgets()

        if sm.settings["auto_load"]:
            self.refresh_levels()

    def on_close(self) -> None:
        logger.info("关闭程序")
        self.destroy()
    
    def _refresh_status_bar(self) -> None:
        self.status_var.set(f"就绪 | 找到 {len(self.level_data)} 个关卡")

    def create_widgets(self) -> None:
        # 工具栏
        lf_toolbar = tb.Labelframe(self, text="工具栏")
        lf_toolbar.pack(fill="x", pady=5)

        buttons: list[tuple] = [
            ("设置", self.open_settings, "primary"),
            ("刷新", self.refresh_levels, "primary"),
            ("保存", self.open_saving, "primary"),
            ("清理缓存", self.clear_cache, "primary"),
            ("管理类型", self.open_types_manager, "primary")
        ]

        for text, command, style in buttons:
            btn = tb.Button(lf_toolbar, text=text, command=command, bootstyle=style)
            btn.pack(side="left", padx=5, pady=5)

        # 关卡列表
        columns: tuple = ("artist", "song", "author", "date")
        headers: tuple = ("艺术家", "歌曲", "作者", "日期")
        widths: tuple = (200, 350, 200, 150)
        anchors: tuple = ("w", "w", "w", "w")

        f_tree = tb.Frame(self)
        f_tree.pack(fill="both", expand=True)
        self.tree, scroller = TreeViewHelper.setup_treeview(f_tree, columns, headers, widths, anchors)
        
        # 设置排序命令
        for col in columns:
            self.tree.heading(
                col, text=headers[columns.index(col)], 
                command=lambda c=col: TreeViewHelper.sort_treeview(self.tree, c))
        # 按照date列逆序排序 - 现在首次点击date列就会默认倒序
        TreeViewHelper.sort_treeview(self.tree, "date")
        
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scroller.pack(side="right", fill="y", pady=5)

        # 进度条
        self.progress = tb.Progressbar(
            self, bootstyle="success-striped", 
            orient="horizontal", mode="determinate"
        )
        self.progress.pack(fill="x", pady=10)

        # 状态栏
        self.status_bar = tb.Label(
            self, 
            textvariable=self.status_var,
            relief="flat",
            anchor="w",
            padding=(10, 5),
            bootstyle="inverse-primary"
        )
        self.status_bar.pack(side="bottom", fill="x")

    def open_settings(self) -> None:
        self.settings_window = Window_Settings(self)
        self.after(0, self.settings_window.focus)

    def open_types_manager(self) -> None:
        self.types_manager_window = Window_Types_Manager(self)
        self.after(0, self.types_manager_window.focus)

    def open_saving(self) -> None:
        self.saving_window = Window_Saving(self)
        # 如果窗口存在(没有被destroy)
        if self.saving_window.winfo_exists():
            self.after(0, self.saving_window.focus)

    def refresh_levels(self) -> None:
        if not sm.settings["zip_folder"]:
            logger.error("请先设置压缩包文件夹")
            self.status_var.set("请先设置压缩包文件夹")
            self.after(0, lambda: Messagebox.show_error("请先设置压缩包文件夹", "错误"))
            return
        if not sm.settings["unzip_cache_folder"]:
            logger.error("请先设置解压缓存文件夹")
            self.status_var.set("请先设置解压缓存文件夹")
            self.after(0, lambda: Messagebox.show_error("请先设置解压缓存文件夹", "错误"))
            return
        
        self.level_data = []
        self.tree.delete(*self.tree.get_children())
        # 清空Level对象映射
        self.tree.level_map.clear()

        def th():
            logger.info("开始刷新关卡")
            self.status_var.set("正在刷新关卡...")
            self.progress["value"] = 0
            try:
                lm: Level_Manager = Level_Manager(self)
                self.level_data = lm.load_levels()
            except Exception as e:
                logger.error(f"刷新关卡时发生未知错误: {e}")
                self.status_var.set("刷新关卡失败")
                self.after(0, lambda e=e: Messagebox.show_error(f"刷新关卡时发生未知错误: {e}", "错误"))
                return
            
            self._refresh_status_bar()
            TreeViewHelper.populate_treeview(self.tree, self.level_data)
        
        threading.Thread(target=th).start()

    def clear_cache(self) -> None:
        if not sm.settings["unzip_cache_folder"]:
            logger.error("请先设置解压缓存文件夹")
            self.status_var.set("请先设置解压缓存文件夹")
            self.after(0, lambda: Messagebox.show_error("请先设置解压缓存文件夹", "错误"))
            return
        
        def th():
            logger.info("开始清理缓存")
            self.status_var.set("正在清理缓存...")
            try:
                FileUtils.clear_directory(sm.settings["unzip_cache_folder"])
                logger.info(f"成功清理缓存文件夹: {sm.settings['unzip_cache_folder']}")
                
            except Exception as e:
                logger.error(f"清理缓存时发生未知错误: {e}")
                self.status_var.set("清理缓存失败")
                self.after(0, lambda e=e: Messagebox.show_error(f"清理缓存时发生未知错误: {e}", "错误"))
                return
            
            self._refresh_status_bar()
            self.status_var.set("缓存已清理")
        
        threading.Thread(target=th).start()

if __name__ == "__main__":
    ui = UI()
    ui.mainloop()