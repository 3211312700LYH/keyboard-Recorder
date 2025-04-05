import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import keyboard
import time
import json
import threading


class RecorderApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("键盘操作录制器 v1.0")
        self.window.geometry("400x300")

        # 创建控件
        self.create_widgets()
        self.recording = False
        self.playing = False

    def create_widgets(self):
        """创建界面元素"""
        # 录制部分
        ttk.Label(self.window, text="录制文件路径:").grid(row=0, column=0, padx=5, pady=5)
        self.record_path = ttk.Entry(self.window, width=25)
        self.record_path.grid(row=0, column=1)
        ttk.Button(self.window, text="浏览", command=self.select_record_file).grid(row=0, column=2)
        self.record_btn = ttk.Button(self.window, text="开始录制", command=self.toggle_record)
        self.record_btn.grid(row=1, column=0, columnspan=3, pady=10)

        # 回放部分
        ttk.Label(self.window, text="回放文件路径:").grid(row=2, column=0, padx=5, pady=5)
        self.play_path = ttk.Entry(self.window, width=25)
        self.play_path.grid(row=2, column=1)
        ttk.Button(self.window, text="浏览", command=self.select_play_file).grid(row=2, column=2)

        ttk.Label(self.window, text="重复次数:").grid(row=3, column=0)
        self.repeat_times = ttk.Combobox(self.window, values=[1, 3, 5, 10, "无限"])
        self.repeat_times.current(0)
        self.repeat_times.grid(row=3, column=1)

        self.play_btn = ttk.Button(self.window, text="开始回放", command=self.toggle_play)
        self.play_btn.grid(row=4, column=0, columnspan=3, pady=10)

        # 状态栏
        self.status = ttk.Label(self.window, text="就绪", relief=tk.SUNKEN)
        self.status.grid(row=5, column=0, columnspan=3, sticky="ew")

    def select_record_file(self):
        """选择录制保存路径"""
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON文件", "*.json")])
        if path:
            self.record_path.delete(0, tk.END)
            self.record_path.insert(0, path)

    def select_play_file(self):
        """选择回放文件"""
        path = filedialog.askopenfilename(filetypes=[("JSON文件", "*.json")])
        if path:
            self.play_path.delete(0, tk.END)
            self.play_path.insert(0, path)

    def toggle_record(self):
        """切换录制状态"""
        if not self.recording:
            path = self.record_path.get()
            if not path:
                messagebox.showerror("错误", "请先选择保存路径")
                return

            self.record_thread = threading.Thread(target=self.start_record, args=(path,))
            self.record_thread.start()
            self.record_btn.config(text="停止录制")
            self.status.config(text="录制中...按ESC停止")
        else:
            self.stop_record()

    def start_record(self, path):
        """开始录制"""
        self.recording = True
        self.events = []
        self.start_time = time.time()

        keyboard.hook(self.record_event)
        keyboard.wait('esc')
        self.stop_record()

        with open(path, 'w') as f:
            json.dump(self.events, f)
        messagebox.showinfo("完成", f"已保存录制文件到\n{path}")

    def stop_record(self):
        """停止录制"""
        keyboard.unhook_all()
        self.recording = False
        self.record_btn.config(text="开始录制")
        self.status.config(text="就绪")

    def record_event(self, event):
        """记录键盘事件"""
        if event.event_type in ('down', 'up'):
            timestamp = time.time() - self.start_time
            self.events.append({
                'type': event.event_type,
                'key': event.name,
                'time': round(timestamp, 3)
            })

    def toggle_play(self):
        """切换回放状态"""
        if not self.playing:
            path = self.play_path.get()
            if not path:
                messagebox.showerror("错误", "请先选择回放文件")
                return

            try:
                with open(path) as f:
                    self.play_data = json.load(f)
            except:
                messagebox.showerror("错误", "文件读取失败")
                return

            repeat = self.repeat_times.get()
            if repeat == "无限":
                repeat = 9999
            else:
                repeat = int(repeat)

            self.play_thread = threading.Thread(target=self.play_record, args=(repeat,))
            self.play_thread.start()
            self.play_btn.config(text="停止回放")
            self.status.config(text="回放中...")
        else:
            self.playing = False
            self.play_btn.config(text="开始回放")
            self.status.config(text="已停止")

    def play_record(self, repeat):
        """执行回放"""
        self.playing = True
        try:
            for _ in range(repeat):
                if not self.playing: break
                start_time = time.time()
                for event in self.play_data:
                    if not self.playing: break
                    while (time.time() - start_time) < event['time']:
                        time.sleep(0.001)

                    if event['type'] == 'down':
                        keyboard.press(event['key'])
                    else:
                        keyboard.release(event['key'])
        finally:
            self.playing = False


if __name__ == "__main__":
    app = RecorderApp()
    app.window.mainloop()


"""
试试第一个项目（？？？）
"""