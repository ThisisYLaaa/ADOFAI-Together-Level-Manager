# 树形视图创建
from CS import Level
from Init_Settings import *

import ttkbootstrap as tb
import tkinter as tk

class CustomTreeview(tb.Treeview):
    """自定义Treeview类，添加level_map属性"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 存储level对象的映射，键为项目ID
        self.level_map = {}

class TreeViewHelper:
    """树形视图工具类"""
    # 用于跟踪每棵树的每列排序状态
    _sort_states = {}
    # 用于跟踪每棵树的上一次排序列
    _last_sorted_col = {}
    
    @staticmethod
    def setup_treeview(parent, columns, headings, widths, anchors, selectmode="extended", bootstyle="primary"):
        tree = CustomTreeview(
            parent, 
            columns=columns, 
            show="headings", 
            selectmode=selectmode,
            bootstyle=bootstyle
        )
        
        for col, heading, width, anchor in zip(columns, headings, widths, anchors):
            tree.heading(col, text=heading)
            tree.column(col, width=width, anchor=anchor)
        
        scrollbar = tb.Scrollbar(parent, orient="vertical", command=tree.yview, bootstyle="round")
        tree.configure(yscrollcommand=scrollbar.set)
        
        # 设置鼠标滚轮滚动
        def _on_mousewheel(event: tk.Event):
            if event.delta:
                tree.yview_scroll(int(-1*(event.delta/120)*SSLC), "units")
        tree.bind("<MouseWheel>", _on_mousewheel)
        
        return tree, scrollbar
    
    @staticmethod
    def sort_treeview(tree: CustomTreeview, col: str):
        """
        对树形视图进行排序，支持点击切换升降序
        :param tree: 自定义树形视图对象
        :param col: 要排序的列名
        """
        # 获取树的唯一标识（使用其内存地址）
        tree_id = id(tree)
        # 初始化当前树的排序状态
        if tree_id not in TreeViewHelper._sort_states:
            TreeViewHelper._sort_states[tree_id] = {}
        if tree_id not in TreeViewHelper._last_sorted_col:
            TreeViewHelper._last_sorted_col[tree_id] = None
        
        # 检查是否点击了新的列
        last_col = TreeViewHelper._last_sorted_col[tree_id]
        if last_col != col:
            # 点击新列，默认正序排序
            reverse = False
            TreeViewHelper._sort_states[tree_id][col] = True  # 下次点击将切换为倒序
            TreeViewHelper._last_sorted_col[tree_id] = col
        else:
            # 点击同一列，切换排序状态
            reverse = TreeViewHelper._sort_states[tree_id].get(col, False)
            TreeViewHelper._sort_states[tree_id][col] = not reverse
        
        # 获取所有行指定列的值与行ID组成的列表
        items = [(tree.set(child, col), child) for child in tree.get_children('')]
        # 根据列值进行升序或降序排序
        items.sort(reverse=reverse)
        # 按排序后的顺序重新移动行到树形视图中
        for index, (val, child) in enumerate(items):
            tree.move(child, '', index)
        
        # 更新表头显示，添加排序指示
        for c in tree['columns']:
            if c == col:
                # 显示排序方向
                heading_text = tree.heading(c, 'text')
                # 移除之前的排序指示
                if ' ↑' in heading_text or ' ↓' in heading_text:
                    heading_text = heading_text[:-2]
                # 添加当前排序指示
                heading_text += ' ↓' if reverse else ' ↑'
                tree.heading(c, text=heading_text)
            else:
                # 移除其他列的排序指示
                heading_text = tree.heading(c, 'text')
                if ' ↑' in heading_text or ' ↓' in heading_text:
                    tree.heading(c, text=heading_text[:-2])
    
    @staticmethod
    def populate_treeview(tree: CustomTreeview, data: list[Level]):
        """
        填充树形视图(没有删除原本的内容)
        :param tree: 自定义树形视图对象
        :param data: 要填充的数据列表
        """
        for item in data:
            # 插入项目并获取项目ID
            item_id = tree.insert('', 'end', values=item.get_display_values())
            # 将项目ID与Level对象关联
            tree.level_map[item_id] = item
        
        TreeViewHelper.sort_treeview(tree, 'date')