import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sys
from morning_report import MorningReport
from evening_report import EveningReport

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    """获取资源绝对路径，兼容打包后的exe"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("广州电力工程监理有限公司 - 日报数据处理")
        self.geometry("1000x800")
        self.minsize(900, 700)

        self.morning_files = {"risk": None, "work": None, "staff": None}
        self.evening_files = {
            "risk": None, "work": None, "staff": None,
            "violation": None, "recorder": None
        }
        self.selected_date_type = "today"

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        self.home_frame = ctk.CTkFrame(self.main_frame)
        self.date_choice_frame = ctk.CTkFrame(self.main_frame)
        self.morning_frame = ctk.CTkFrame(self.main_frame)
        self.evening_frame = ctk.CTkFrame(self.main_frame)

        self.setup_home_page()
        self.setup_date_choice_page()
        self.setup_morning_page()
        self.setup_evening_page()

        self.show_home()

    def setup_home_page(self):
        title = ctk.CTkLabel(self.home_frame, text="广州电力工程监理有限公司 —— 日报数据处理",
                             font=ctk.CTkFont(size=28, weight="bold"), text_color="#165DFF")
        title.pack(pady=60)

        btn_frame = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        btn_frame.pack(expand=True)

        btn1 = ctk.CTkButton(btn_frame, text="早报数据处理", width=300, height=60,
                             font=ctk.CTkFont(size=20), corner_radius=15,
                             fg_color="#165DFF", hover_color="#0E42CC",
                             command=self.show_date_choice)
        btn1.pack(pady=30)

        btn2 = ctk.CTkButton(btn_frame, text="晚报数据处理", width=300, height=60,
                             font=ctk.CTkFont(size=20), corner_radius=15,
                             fg_color="#165DFF", hover_color="#0E42CC",
                             command=self.show_evening)
        btn2.pack(pady=30)

    def setup_date_choice_page(self):
        title = ctk.CTkLabel(self.date_choice_frame, text="选择处理日期",
                             font=ctk.CTkFont(size=28, weight="bold"), text_color="#165DFF")
        title.pack(pady=60)

        btn_frame = ctk.CTkFrame(self.date_choice_frame, fg_color="transparent")
        btn_frame.pack(expand=True)

        btn_prev = ctk.CTkButton(btn_frame, text="前一日", width=300, height=60,
                                 font=ctk.CTkFont(size=20), corner_radius=15,
                                 fg_color="#165DFF", hover_color="#0E42CC",
                                 command=lambda: self.set_date_and_go_to_morning("yesterday"))
        btn_prev.pack(pady=30)

        btn_today = ctk.CTkButton(btn_frame, text="今日", width=300, height=60,
                                  font=ctk.CTkFont(size=20), corner_radius=15,
                                  fg_color="#165DFF", hover_color="#0E42CC",
                                  command=lambda: self.set_date_and_go_to_morning("today"))
        btn_today.pack(pady=30)

        back_btn = ctk.CTkButton(self.date_choice_frame, text="返回首页", width=150, height=40,
                                 font=ctk.CTkFont(size=16), command=self.show_home)
        back_btn.pack(pady=20)

    def set_date_and_go_to_morning(self, date_type):
        self.selected_date_type = date_type
        self.show_morning()

    def setup_morning_page(self):
        header = ctk.CTkFrame(self.morning_frame, fg_color="transparent")
        header.pack(fill="x", pady=20, padx=30)
        back_btn = ctk.CTkButton(header, text="← 选择其他日期", width=120, command=self.show_date_choice)
        back_btn.pack(side="left")
        title = ctk.CTkLabel(header, text="早报数据处理", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(side="left", expand=True)

        self.date_type_label = ctk.CTkLabel(self.morning_frame, text="", font=ctk.CTkFont(size=14))
        self.date_type_label.pack(pady=5)

        sub_frame = ctk.CTkFrame(self.morning_frame, fg_color="transparent")
        sub_frame.pack(pady=10)
        ctk.CTkLabel(sub_frame, text="请上传以下文件", font=ctk.CTkFont(size=16)).pack()

        self.morning_risk_frame = self.create_file_selector(self.morning_frame, "风险管控到位列表", "risk", self.morning_files)
        self.morning_work_frame = self.create_file_selector(self.morning_frame, "作业统计详情", "work", self.morning_files)
        self.morning_staff_frame = self.create_file_selector(self.morning_frame, "监理人员整体应用数据列表", "staff", self.morning_files)

        # 输出目录选择
        output_frame = ctk.CTkFrame(self.morning_frame, fg_color="transparent")
        output_frame.pack(pady=10, padx=50, fill="x")
        ctk.CTkLabel(output_frame, text="导出结果保存目录：", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        self.morning_output_var = ctk.StringVar(value=os.path.join(os.getcwd(), "输出"))
        output_entry = ctk.CTkEntry(output_frame, textvariable=self.morning_output_var, state="readonly", width=300)
        output_entry.pack(side="left", padx=5)
        ctk.CTkButton(output_frame, text="浏览", width=80, command=self.select_morning_output_dir).pack(side="left", padx=5)

        btn_frame = ctk.CTkFrame(self.morning_frame, fg_color="transparent")
        btn_frame.pack(pady=30)
        self.morning_confirm_btn = ctk.CTkButton(btn_frame, text="确定", width=120, command=self.morning_confirm)
        self.morning_confirm_btn.pack(side="left", padx=20)
        self.morning_cancel_btn = ctk.CTkButton(btn_frame, text="取消", width=120, fg_color="gray", command=self.morning_cancel)
        self.morning_cancel_btn.pack(side="left", padx=20)

    def select_morning_output_dir(self):
        dir_selected = filedialog.askdirectory(title="选择导出结果保存目录")
        if dir_selected:
            self.morning_output_var.set(dir_selected)

    def setup_evening_page(self):
        header = ctk.CTkFrame(self.evening_frame, fg_color="transparent")
        header.pack(fill="x", pady=20, padx=30)
        back_btn = ctk.CTkButton(header, text="← 返回首页", width=100, command=self.show_home)
        back_btn.pack(side="left")
        title = ctk.CTkLabel(header, text="晚报数据处理", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(side="left", expand=True)

        sub_frame = ctk.CTkFrame(self.evening_frame, fg_color="transparent")
        sub_frame.pack(pady=10)
        ctk.CTkLabel(sub_frame, text="今日（16时数据）", font=ctk.CTkFont(size=16)).pack()

        self.evening_risk_frame = self.create_file_selector(self.evening_frame, "风险管控到位列表 (今日16时)", "risk", self.evening_files)
        self.evening_work_frame = self.create_file_selector(self.evening_frame, "作业统计详情", "work", self.evening_files)
        self.evening_staff_frame = self.create_file_selector(self.evening_frame, "监理人员整体应用数据列表", "staff", self.evening_files)

        self.evening_violation_frame = self.create_file_selector(self.evening_frame, "履职表单督查导出（无图）", "violation", self.evening_files)
        self.evening_recorder_frame = self.create_file_selector(self.evening_frame, "监理见证记录仪日数据汇总", "recorder", self.evening_files)

        # 输出目录选择
        output_frame = ctk.CTkFrame(self.evening_frame, fg_color="transparent")
        output_frame.pack(pady=10, padx=50, fill="x")
        ctk.CTkLabel(output_frame, text="导出结果保存目录：", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        self.evening_output_var = ctk.StringVar(value=os.path.join(os.getcwd(), "输出"))
        output_entry = ctk.CTkEntry(output_frame, textvariable=self.evening_output_var, state="readonly", width=300)
        output_entry.pack(side="left", padx=5)
        ctk.CTkButton(output_frame, text="浏览", width=80, command=self.select_evening_output_dir).pack(side="left", padx=5)

        btn_frame = ctk.CTkFrame(self.evening_frame, fg_color="transparent")
        btn_frame.pack(pady=30)
        self.evening_confirm_btn = ctk.CTkButton(btn_frame, text="确定", width=120, command=self.evening_confirm)
        self.evening_confirm_btn.pack(side="left", padx=20)
        self.evening_cancel_btn = ctk.CTkButton(btn_frame, text="取消", width=120, fg_color="gray", command=self.evening_cancel)
        self.evening_cancel_btn.pack(side="left", padx=20)

    def select_evening_output_dir(self):
        dir_selected = filedialog.askdirectory(title="选择导出结果保存目录")
        if dir_selected:
            self.evening_output_var.set(dir_selected)

    def create_file_selector(self, parent, label_text, file_key, files_dict):
        frame = ctk.CTkFrame(parent, corner_radius=10, border_width=1, border_color="#165DFF")
        frame.pack(pady=10, padx=50, fill="x")
        ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=14)).pack(anchor="w", padx=10, pady=(10, 0))

        path_var = ctk.StringVar()
        entry = ctk.CTkEntry(frame, textvariable=path_var, state="readonly")
        entry.pack(side="left", fill="x", expand=True, padx=10, pady=5)

        def browse():
            file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xls *.xlsx")])
            if file_path:
                files_dict[file_key] = file_path
                path_var.set(os.path.basename(file_path))
        ctk.CTkButton(frame, text="浏览", width=80, command=browse).pack(side="right", padx=10, pady=5)

        frame.path_var = path_var
        frame.file_key = file_key
        return frame

    def morning_confirm(self):
        if not all(self.morning_files.values()):
            messagebox.showwarning("文件缺失", "请选择三个文件：风险表、作业表、人员表")
            return

        self.morning_confirm_btn.configure(state="disabled", text="处理中...")
        self.morning_cancel_btn.configure(state="disabled")
        self.update_idletasks()

        output_dir = self.morning_output_var.get()

        try:
            report = MorningReport(date_type=self.selected_date_type, output_dir=output_dir)
            report.process_with_files(
                self.morning_files["risk"],
                self.morning_files["work"],
                self.morning_files["staff"]
            )
            messagebox.showinfo("完成", f"导出结果已存储至：{output_dir}")
            self.morning_cancel()
            self.show_date_choice()
        except Exception as e:
            messagebox.showerror("错误", f"处理失败：{str(e)}")
        finally:
            if hasattr(self, 'morning_confirm_btn') and self.morning_confirm_btn.winfo_exists():
                self.morning_confirm_btn.configure(state="normal", text="确定")
                self.morning_cancel_btn.configure(state="normal")

    def morning_cancel(self):
        for key in self.morning_files:
            self.morning_files[key] = None
        for frame in [self.morning_risk_frame, self.morning_work_frame, self.morning_staff_frame]:
            if hasattr(frame, 'path_var'):
                frame.path_var.set("")

    def evening_confirm(self):
        required = ["risk", "work", "staff"]
        for k in required:
            if not self.evening_files.get(k):
                messagebox.showwarning("文件缺失", f"请选择{ ['风险表','作业表','人员表'][required.index(k)] }文件")
                return

        self.evening_confirm_btn.configure(state="disabled", text="处理中...")
        self.evening_cancel_btn.configure(state="disabled")
        self.update_idletasks()

        output_dir = self.evening_output_var.get()

        try:
            report = EveningReport(output_dir=output_dir)
            report.process_with_files(
                self.evening_files["risk"],
                self.evening_files["work"],
                self.evening_files["staff"],
                violation_file=self.evening_files.get("violation"),
                recorder_file=self.evening_files.get("recorder")
            )
            messagebox.showinfo("完成", f"导出结果已存储至：{output_dir}")
            self.evening_cancel()
        except Exception as e:
            messagebox.showerror("错误", f"处理失败：{str(e)}")
        finally:
            if hasattr(self, 'evening_confirm_btn') and self.evening_confirm_btn.winfo_exists():
                self.evening_confirm_btn.configure(state="normal", text="确定")
                self.evening_cancel_btn.configure(state="normal")

    def evening_cancel(self):
        for key in self.evening_files:
            self.evening_files[key] = None
        for frame in [self.evening_risk_frame, self.evening_work_frame, self.evening_staff_frame,
                      self.evening_violation_frame, self.evening_recorder_frame]:
            if hasattr(frame, 'path_var'):
                frame.path_var.set("")

    def show_home(self):
        self.hide_all()
        self.home_frame.pack(fill="both", expand=True)

    def show_date_choice(self):
        self.hide_all()
        self.date_choice_frame.pack(fill="both", expand=True)

    def show_morning(self):
        if self.selected_date_type == "yesterday":
            self.date_type_label.configure(text="当前处理：前一日数据")
        else:
            self.date_type_label.configure(text="当前处理：今日数据")
        self.hide_all()
        self.morning_frame.pack(fill="both", expand=True)

    def show_evening(self):
        self.hide_all()
        self.evening_frame.pack(fill="both", expand=True)

    def hide_all(self):
        self.home_frame.pack_forget()
        self.date_choice_frame.pack_forget()
        self.morning_frame.pack_forget()
        self.evening_frame.pack_forget()

if __name__ == "__main__":
    app = App()
    app.mainloop()