import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
from database import insert_problem, calculate_next_review, get_today_reviews, update_review_status, get_all_problems

# GUI界面
class LeetCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LeetCode刷题记录系统")

        # 题目输入
        tk.Label(root, text="题目编号和名称").grid(row=0)
        self.problem_entry = tk.Entry(root)
        self.problem_entry.grid(row=0, column=1)

        # 题目难度
        tk.Label(root, text="题目难度").grid(row=1)
        self.difficulty = tk.StringVar()
        tk.OptionMenu(root, self.difficulty, "easy", "medium", "hard").grid(row=1, column=1)

        # 解题状态
        tk.Label(root, text="解题状态").grid(row=2)
        self.status = tk.StringVar()
        tk.OptionMenu(root, self.status, "unsolved", "solved", "reviewed").grid(row=2, column=1)

        # 提交按钮
        tk.Button(root, text="提交", command=self.submit).grid(row=3, column=1)

        # 复习表格
        self.tree = ttk.Treeview(root, columns=("id", "leetcode_id", "title", "difficulty", "status", "action"), show='headings')
        self.tree.heading("id", text="ID")
        self.tree.heading("leetcode_id", text="LeetCode编号")
        self.tree.heading("title", text="题目名称")
        self.tree.heading("difficulty", text="难度")
        self.tree.heading("status", text="状态")
        self.tree.heading("action", text="操作")
        self.tree.column("action", width=100)
        self.tree.grid(row=4, column=0, columnspan=4)

        # 分页按钮
        self.page = 0
        self.page_size = 5
        tk.Button(root, text="上一页", command=self.prev_page).grid(row=5, column=0)
        tk.Button(root, text="下一页", command=self.next_page).grid(row=5, column=1)
        tk.Button(root, text="显示所有题目", command=self.show_all_problems).grid(row=5, column=2)
        tk.Button(root, text="显示今日复习", command=self.load_reviews).grid(row=5, column=3)

        self.load_reviews()

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
        next_review = calculate_next_review(solve_date, 0)

        if not insert_problem(leetcode_id, title, difficulty, status, solve_date, next_review):
            messagebox.showerror("错误", "题目已经存在")
            return

        messagebox.showinfo("提示", "题目信息已记录")
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
            button = tk.Button(self.root, text="已复习", command=lambda problem_id=problem_id: self.mark_as_reviewed(problem_id))
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
    root = tk.Tk()
    app = LeetCodeApp(root)
    root.mainloop()