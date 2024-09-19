import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
from database import insert_problem, calculate_next_review, get_today_reviews, update_review_status, get_all_problems
from config import save_config, load_config
from generate_config import get_database_config

# GUI界面
class LeetCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LeetCode刷题记录系统")

        self.main_frame = ttk.Frame(root, padding="10 10 10 10")
        self.main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

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

        # 添加主题选择
        self.themes = ttk.Style().theme_names()
        ttk.Label(self.main_frame, text="主题").grid(row=0, column=0, sticky=tk.E, padx=(0, 5))
        self.theme_combobox = ttk.Combobox(self.main_frame, values=self.themes, width=15)
        self.theme_combobox.set(self.root.style.theme.name)
        self.theme_combobox.grid(row=0, column=1, sticky=tk.W)
        self.theme_combobox.bind("<<ComboboxSelected>>", self.change_theme)

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
        ttk.Button(self.main_frame, text="提交", command=self.submit).grid(row=3, column=2, padx=(10, 0), pady=(5, 0))

        ttk.Separator(self.main_frame, orient="horizontal", bootstyle="info").grid(row=4, columnspan=3, sticky="ew", pady=10)

        # 复习表格
        self.tree = ttk.Treeview(self.main_frame, columns=("leetcode_id", "title", "difficulty", "status", "action"), show='headings')
        self.tree.heading("leetcode_id", text="LeetCode编号")
        self.tree.heading("title", text="题目名称")
        self.tree.heading("difficulty", text="难度")
        self.tree.heading("status", text="状态")
        self.tree.heading("action", text="操作")
        self.tree.column("action", width=100)
        self.tree.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 分页按钮
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(10, 0))

        self.page = 0
        self.page_size = 5
        ttk.Button(button_frame, text="上一页", command=self.prev_page).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="下一页", command=self.next_page).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="显示所有题目", command=self.show_all_problems).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="显示今日复习", command=self.load_reviews).grid(row=0, column=3, padx=5)

        self.load_reviews()

        # 配置列和行的权重，使其能够随窗口调整大小
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(5, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def change_theme(self, event):
        selected_theme = self.theme_combobox.get()
        self.root.style.theme_use(selected_theme)
        save_config(selected_theme)

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
            self.tree.insert("", "end", values=review + ("",))
        self.add_review_buttons()

    def add_review_buttons(self):
        for i, item in enumerate(self.tree.get_children()):
            problem_id = self.tree.item(item, "values")[0]
            button = ttk.Button(self.root, text="已复习", command=lambda problem_id=problem_id: self.mark_as_reviewed(problem_id))
            self.tree.set(item, column="action", value=button)
            self.tree.item(item, tags=("button",))
        self.tree.tag_bind("button", "<Button-1>", self.on_button_click)

    def on_button_click(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if column == "#6":  # "action" column
            problem_id = self.tree.item(item, "values")[0]
            self.mark_as_reviewed(problem_id)

    def mark_as_reviewed(self, problem_id):
        update_review_status(problem_id)
        self.load_reviews()

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

if __name__ == "__main__":
    config = load_config()
    root = ttk.Window(themename=config['theme'])
    app = LeetCodeApp(root)
    root.mainloop()