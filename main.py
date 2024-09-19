import tkinter as tk
from tkinter import messagebox, font as tkfont
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
from database import insert_problem, calculate_next_review, get_today_reviews, update_review_status, get_all_problems, get_next_review_date
from config import save_config, load_config
from generate_config import get_database_config

# GUI界面
class LeetCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LeetCode刷题记录系统")

        self.main_frame = ttk.Frame(root, padding="10 10 10 10")
        self.main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 定义字体大小相关的属性
        self.font_sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20]
        self.current_font_size = 10  # 默认字体大小
        self.current_font_family = 'TkDefaultFont'  # 默认字体
        self.available_fonts = list(set(tkfont.families()))
        self.available_fonts.sort()

        self.db_config = None
        self.check_database_config()

    def check_database_config(self):
        self.db_config = get_database_config()
        if not self.db_config:
            self.show_db_config_error()
        else:
            self.create_main_interface()

    def show_db_config_error(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.main_frame, text="数据库配置失败").grid(row=0, column=0, pady=10)
        ttk.Button(self.main_frame, text="重试", command=self.check_database_config).grid(row=1, column=0)

    def create_main_interface(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # 创建一个新的框架来容纳主题、字体和字体大小选择
        settings_frame = ttk.LabelFrame(self.main_frame, text="设置", padding="5 5 5 5")
        settings_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        settings_frame.columnconfigure(5, weight=1)

        # 主题选择
        ttk.Label(settings_frame, text="主题").grid(row=0, column=0, sticky="e", padx=(0, 5))
        self.theme_combobox = ttk.Combobox(settings_frame, values=ttk.Style().theme_names(), width=15)
        self.theme_combobox.set(self.root.style.theme.name)
        self.theme_combobox.grid(row=0, column=1, sticky="w")
        self.theme_combobox.bind("<<ComboboxSelected>>", self.change_theme)

        # 字体选择
        ttk.Label(settings_frame, text="字体").grid(row=0, column=2, sticky="e", padx=(10, 5))
        self.font_combobox = ttk.Combobox(settings_frame, values=self.available_fonts, width=15)
        self.font_combobox.set(self.current_font_family)
        self.font_combobox.grid(row=0, column=3, sticky="w")
        self.font_combobox.bind("<<ComboboxSelected>>", self.change_font)

        # 字体大小选择
        ttk.Label(settings_frame, text="字体大小").grid(row=0, column=4, sticky="e", padx=(10, 5))
        self.font_size_combobox = ttk.Combobox(settings_frame, values=self.font_sizes, width=5)
        self.font_size_combobox.set(self.current_font_size)
        self.font_size_combobox.grid(row=0, column=5, sticky="w")
        self.font_size_combobox.bind("<<ComboboxSelected>>", self.change_font_size)

        # 题目输入
        ttk.Label(self.main_frame, text="题目编号和名称").grid(row=1, column=0, sticky=tk.E, padx=(0, 5), pady=(10, 0))
        self.problem_entry = ttk.Entry(self.main_frame, width=35)
        self.problem_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=(10, 0))

        # 题目难度
        ttk.Label(self.main_frame, text="题目难度").grid(row=2, column=0, sticky=tk.E, padx=(0, 5), pady=(5, 0))
        self.difficulty = ttk.Combobox(self.main_frame, values=['', 'easy', 'medium', 'hard'], bootstyle="primary", width=20)
        self.difficulty.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))

        # 解题状态
        ttk.Label(self.main_frame, text="解题状态").grid(row=3, column=0, sticky=tk.E, padx=(0, 5), pady=(5, 0))
        self.status = ttk.Combobox(self.main_frame, values=['', 'solved', 'reviewed'], bootstyle="primary", width=20)
        self.status.grid(row=3, column=1, sticky=tk.W, pady=(5, 0))

        # 提交按钮
        ttk.Button(self.main_frame, text="提交", command=self.submit, style='Large.TButton').grid(row=3, column=2, padx=(10, 0), pady=(5, 0))

        ttk.Separator(self.main_frame, orient="horizontal", bootstyle="info").grid(row=4, columnspan=3, sticky="ew", pady=10)

        # 复习表格
        self.tree = ttk.Treeview(self.main_frame, columns=("leetcode_id", "title", "difficulty", "next_review", "action"), show='headings')
        self.tree.heading("leetcode_id", text="LeetCode编号")
        self.tree.heading("title", text="题目名称")
        self.tree.heading("difficulty", text="难度")
        self.tree.heading("next_review", text="下次复习时间")
        self.tree.heading("action", text="操作")
        
        # 设置列的宽度和对齐方式
        self.tree.column("leetcode_id", width=100, anchor="center")
        self.tree.column("title", width=200, anchor="center")
        self.tree.column("difficulty", width=100, anchor="center")
        self.tree.column("next_review", width=100, anchor="center")
        self.tree.column("action", width=100, anchor="center")
        
        # 添加分隔线
        self.tree.configure(style="Treeview")
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        
        self.tree.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 分页按钮
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(10, 0))

        self.page = 0
        self.page_size = 5
        ttk.Button(button_frame, text="上一页", command=self.prev_page, style='Large.TButton').grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="下一页", command=self.next_page, style='Large.TButton').grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="显示所有题目", command=self.show_all_problems, style='Large.TButton').grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="显示今日复习", command=self.load_reviews, style='Large.TButton').grid(row=0, column=3, padx=5)

        self.load_reviews()

        # 配置列和行的权重，使其能够随窗口调整大小
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(5, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # 初始化字体大小
        self.update_font()

    def change_theme(self, event):
        selected_theme = self.theme_combobox.get()
        self.root.style.theme_use(selected_theme)
        save_config(selected_theme)
        self.update_font()  # 在更改主题后更新字体大小

    def change_font(self, event):
        selected_font = self.font_combobox.get()
        self.current_font_family = selected_font
        self.update_font()

    def change_font_size(self, event):
        selected_size = int(self.font_size_combobox.get())
        self.current_font_size = selected_size
        self.update_font()

    def update_font(self):
        style = ttk.Style()
        font_tuple = (self.current_font_family, self.current_font_size)
        
        style.configure('.', font=font_tuple)
        style.configure('Treeview', font=font_tuple)
        style.configure('Treeview.Heading', font=(self.current_font_family, self.current_font_size, 'bold'))
        style.configure('TLabelframe.Label', font=font_tuple)
        style.configure('TLabelframe', font=font_tuple)
        style.configure('Large.TButton', font=font_tuple)

        self.problem_entry.configure(font=font_tuple)
        self.difficulty.configure(font=font_tuple)
        self.status.configure(font=font_tuple)
        self.theme_combobox.configure(font=font_tuple)
        self.font_combobox.configure(font=font_tuple)
        self.font_size_combobox.configure(font=font_tuple)

        style.configure('Treeview', rowheight=self.current_font_size * 2)

        self.root.update()

    def submit(self):
        problem_text = self.problem_entry.get()
        try:
            leetcode_id, title = problem_text.split(". ", 1)
        except ValueError:
            messagebox.showerror("错误", "请输入正确的题目编号和名称，格式为：编号. 名称")
            return

        difficulty = self.difficulty.get()
        status = self.status.get()
        solve_date = datetime.now().date()
        next_review = calculate_next_review(solve_date, 0, difficulty)

        if insert_problem(leetcode_id, title, difficulty, status, solve_date, next_review):
            messagebox.showinfo("提示", "题目信息已记录或更新")
        else:
            messagebox.showerror("错误", "插入或更新题目失败")
        self.load_reviews()

    def load_reviews(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        reviews = get_today_reviews()
        start = self.page * self.page_size
        end = start + self.page_size
        for review in reviews[start:end]:
            self.tree.insert("", "end", values=review + ("已复习",), tags=("review_button",))
        self.tree.tag_bind("review_button", "<Button-1>", self.on_button_click)
        self.update_font()  # 在加载数据后更新字体大小

    def on_button_click(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if column == "#5":  # "action" column
            problem_id = self.tree.item(item, "values")[0]
            self.mark_as_reviewed(problem_id)

    def mark_as_reviewed(self, problem_id):
        if update_review_status(problem_id):
            self.load_reviews()
        else:
            messagebox.showerror("错误", "更新复习状态失败")

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.load_reviews()

    def next_page(self):
        reviews = get_today_reviews()
        if (self.page + 1) * self.page_size < len(reviews):
            self.page += 1
            self.load_reviews()

    def show_all_problems(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        problems = get_all_problems()
        for problem in problems:
            self.tree.insert("", "end", values=problem)
        self.update_font()  # 在显示所有问题后更新字体大小

if __name__ == "__main__":
    config = load_config()
    root = ttk.Window(themename=config['theme'])
    app = LeetCodeApp(root)
    root.mainloop()