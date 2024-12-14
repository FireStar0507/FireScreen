import mss
import mss.tools
import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import os
import time
import pyautogui


# 获取屏幕大小
def get_screen_size():
    with mss.mss() as sct:
        return (sct.monitors[1]['width'], sct.monitors[1]['height'])


# 定义编码器
codecs = {
    'MP4': cv2.VideoWriter_fourcc(*'mp4v'),
    'AVI': cv2.VideoWriter_fourcc(*'XVID'),
    'MKV': cv2.VideoWriter_fourcc(*'X264'),
    'MOV': cv2.VideoWriter_fourcc(*'avc1'),
    'WMV': cv2.VideoWriter_fourcc(*'WMV1'),
    'FLV': cv2.VideoWriter_fourcc(*'FLV1'),
    'WEBM': cv2.VideoWriter_fourcc(*'vp80'),
}


class ScreenRecorderApp:
    def __init__(self, master):
        self.master = master
        self.recording = False
        self.output_writer = None
        self.start_time = None
        self.fps = 20
        self.frame_interval = 1.0 / self.fps
        self.auto_minimize_screenshot = False
        self.cursor_size = 10
        self.cursor_color = (0, 255, 0)
        self.screen_size = get_screen_size()
        
        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.master)
        frame.pack()

        self.record_button_text = tk.StringVar(value="开始录制")
        
        record_button = tk.Button(frame, textvariable=self.record_button_text, command=self.toggle_recording)
        record_button.pack(side=tk.LEFT)
        
        tk.Button(frame, text="截图", command=self.take_screenshot).pack(side=tk.LEFT)
        tk.Button(frame, text="设置", command=self.open_settings).pack(side=tk.LEFT)
        tk.Button(frame, text="关于", command=self.show_about).pack(side=tk.LEFT)

        self.console = tk.Text(self.master, height=15, width=80)
        self.console.pack(padx=10, pady=10)

    def show_about(self):
        about_message = "FireScreen 火屏 v.2.10\n\n"
        about_message += "这是一个简单的屏幕录制工具，\n"
        about_message += "支持多种视频格式和截图功能。\n"
        about_message += "您可以通过设置帧率和光标颜色来定制录制体验。\n\n"
        about_message += "开发者: FireStar0507\n"
        about_message += "邮箱：18064625480@163.com\n"
        about_message += "Github：FireSrar0507\n"

        messagebox.showinfo("关于", about_message)

    def log_message(self, msg):
        self.console.insert(tk.END, msg + '\n')
        self.console.see(tk.END)

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        if self.recording: return

        self.recording = True
        self.start_time = time.time()
        self.record_button_text.set("停止录制")
        self.log_message("开始录制...")

        output_file = self.select_output_file()
        if output_file is None:
            self.recording = False
            return

        codec = self.get_codec_from_file(output_file)
        if codec is None:
            messagebox.showerror("错误", "不支持的文件格式！")
            self.recording = False
            return

        self.output_writer = cv2.VideoWriter(output_file, codec, self.fps, self.screen_size)
        self.record_screen()

    def select_output_file(self):
        return filedialog.asksaveasfilename(defaultextension='.mp4',
                                              filetypes=[("MP4 files", "*.mp4"),
                                                         ("AVI files", "*.avi"),
                                                         ("MKV files", "*.mkv"),
                                                         ("MOV files", "*.mov"),
                                                         ("WMV files", "*.wmv"),
                                                         ("FLV files", "*.flv"),
                                                         ("WEBM files", "*.webm")])

    def get_codec_from_file(self, output_file):
        file_extension = os.path.splitext(output_file)[1].lower()
        return codecs.get(file_extension[1:].upper())

    def stop_recording(self):
        if not self.recording: return

        self.recording = False
        self.record_button_text.set("开始录制")
        self.log_message("已停止录制。")

        if self.output_writer is not None:
            self.output_writer.release()
            self.output_writer = None

    def record_screen(self):
        if self.recording and self.output_writer is not None:
            with mss.mss() as sct:
                monitor = {'top': 0, 'left': 0, 'width': self.screen_size[0], 'height': self.screen_size[1]}
                img = sct.grab(monitor)
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                mouse_x, mouse_y = pyautogui.position()
                cv2.circle(frame, (mouse_x, mouse_y), self.cursor_size, self.cursor_color, -1)

                self.output_writer.write(frame)

            self.master.after(int(self.frame_interval * 1000), self.record_screen)

    def take_screenshot(self):
        if self.auto_minimize_screenshot:
            self.master.iconify()

        output_file = filedialog.asksaveasfilename(defaultextension='.png',
                                                     filetypes=[("PNG files", "*.png"),
                                                                ("JPEG files", "*.jpg"),
                                                                ("All files", "*.*")])
        if not output_file:
            if self.auto_minimize_screenshot:
                self.master.deiconify()
            return

        with mss.mss() as sct:
            monitor = {'top': 0, 'left': 0, 'width': self.screen_size[0], 'height': self.screen_size[1]}
            img = sct.grab(monitor)
            mss.tools.to_png(img.rgb, img.size, output=output_file)
            self.log_message(f"截图已保存：{output_file}")

        if self.auto_minimize_screenshot:
            self.master.deiconify()

    def open_settings(self):
        # 计算主窗口的当前宽度和高度
        main_width = self.master.winfo_width()
        main_height = self.master.winfo_height()

        self.settings_window = tk.Toplevel(self.master)
        self.settings_window.title("设置")
        self.settings_window.geometry(f"{main_width // 2}x{main_height * 2}")

        tk.Label(self.settings_window, text="设置帧率：").pack(padx=10, pady=5)
        fps_entry = tk.Entry(self.settings_window)
        fps_entry.insert(0, str(self.fps))
        fps_entry.pack(padx=10, pady=5)

        self.auto_minimize_var = tk.BooleanVar(value=self.auto_minimize_screenshot)
        tk.Checkbutton(self.settings_window, text="截屏时自动最小化窗口", variable=self.auto_minimize_var).pack(padx=10, pady=5)

        tk.Label(self.settings_window, text="设置光标大小：").pack(padx=10, pady=5)
        cursor_size_entry = tk.Entry(self.settings_window)
        cursor_size_entry.insert(0, str(self.cursor_size))
        cursor_size_entry.pack(padx=10, pady=5)

        tk.Button(self.settings_window, text="选择光标颜色", command=self.choose_color).pack(padx=10, pady=5)
        tk.Button(self.settings_window, text="确认", command=lambda: self.apply_settings(fps_entry.get(), cursor_size_entry.get())).pack(pady=10)

    def choose_color(self):
        color = colorchooser.askcolor(title="选择光标颜色")
        if color[1]:
            self.cursor_color = color[0]

    def apply_settings(self, fps_entry, cursor_size_entry):
        try:
            fps = int(fps_entry)
            cursor_size = int(cursor_size_entry)

            if fps <= 0 or cursor_size <= 0:
                raise ValueError("帧率和光标大小必须都是正整数。")

            self.fps = fps
            self.frame_interval = 1.0 / self.fps
            self.auto_minimize_screenshot = self.auto_minimize_var.get()
            self.cursor_size = cursor_size

            self.log_message(f"已设置录制帧率为：{self.fps}")

            self.settings_window.destroy()
        except ValueError as e:
            messagebox.showerror("错误", str(e) or "请输入有效的帧率或光标大小.")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("FireScreen 火屏 v.2.10")

    screen_size = get_screen_size()
    window_width = max(int(screen_size[0] // 4.5), 350)
    window_height = max(int(screen_size[1] // 4.5), 240)
    #print(window_width, window_height)
    root.geometry(f"{window_width}x{window_height}")

    app = ScreenRecorderApp(root)
    root.mainloop()