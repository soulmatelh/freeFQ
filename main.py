import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from faster_whisper import WhisperModel

# 支持的媒体后缀
SUPPORTED_EXTENSIONS = ('.wav', '.mp3', '.m4a', '.flac', '.mp4', '.mkv', '.avi', '.mov')

def format_timestamp(seconds: float):
    """将秒数转换为 SRT 标准时间格式: HH:MM:SS,mmm"""
    td_hours = int(seconds // 3600)
    td_mins = int((seconds % 3600) // 60)
    td_secs = int(seconds % 60)
    td_msecs = int(round((seconds % 1) * 1000))
    return f"{td_hours:02}:{td_mins:02}:{td_secs:02},{td_msecs:03}"

class WhisperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kotoba-Whisper 字幕生成工具")
        self.root.geometry("600x500")
        self.export_dir = "" # 自定义输出路径

        # --- UI 布局 ---
        tk.Label(root, text="Kotoba-Whisper 引擎 (SRT 字幕版)", font=("微软雅黑", 12, "bold"), pady=10).pack()

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate", variable=self.progress_var)
        self.progress.pack(pady=5)

        # 状态与路径显示
        self.status_var = tk.StringVar(value="准备就绪")
        tk.Label(root, textvariable=self.status_var, fg="#2c3e50").pack()
        
        self.path_var = tk.StringVar(value="输出位置: 默认(源文件目录)")
        tk.Label(root, textvariable=self.path_var, fg="gray", font=("微软雅黑", 9)).pack()

        # 日志解读区域
        self.log_text = tk.Text(root, height=12, width=70, state='disabled', font=("Consolas", 9), bg="#f8f9fa")
        self.log_text.pack(pady=10, padx=10)
        
        # 按钮容器
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="1. 设置保存目录", command=self.set_export_dir, width=15, bg="#e1f5fe").grid(row=0, column=0, padx=5)
        self.btn_file = tk.Button(btn_frame, text="2. 选择文件并开始", command=self.select_file, width=15, bg="#c8e6c9")
        self.btn_file.grid(row=0, column=1, padx=5)
        self.btn_dir = tk.Button(btn_frame, text="2. 批量处理文件夹", command=self.select_folder, width=15, bg="#fff9c4")
        self.btn_dir.grid(row=0, column=2, padx=5)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def set_export_dir(self):
        """设置最后的输出位置"""
        selected = filedialog.askdirectory()
        if selected:
            self.export_dir = selected
            self.path_var.set(f"输出位置: {selected}")
            self.log(f"设置保存目录为: {selected}")

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("媒体文件", "*.wav *.mp3 *.mp4 *.mkv *.m4a")])
        if path:
            threading.Thread(target=self.run_task, args=(path,), daemon=True).start()

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            threading.Thread(target=self.run_task, args=(path,), daemon=True).start()

    def run_task(self, input_path):
        self.btn_file.config(state="disabled")
        self.btn_dir.config(state="disabled")
        model_path = "./kotoba-whisper-v2.2-faster"

        try:
            self.log(">>> 引擎启动中...")
            device = "cuda" if os.path.exists(os.path.join(os.environ.get("PROGRAMFILES", ""), "NVIDIA GPU Computing Toolkit")) else "cpu"
            model = WhisperModel(model_path, device=device, compute_type="float32")

            files = [input_path] if os.path.isfile(input_path) else [os.path.join(input_path, f) for f in os.listdir(input_path) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
            
            for i, file in enumerate(files):
                file_name = os.path.basename(file)
                self.log(f"\n正在处理 ({i+1}/{len(files)}): {file_name}")
                
                segments, info = model.transcribe(file, language="ja", chunk_length=15)
                
                # 确定保存路径
                base_name = os.path.splitext(file_name)[0] + ".srt"
                save_path = os.path.join(self.export_dir if self.export_dir else os.path.dirname(file), base_name)

                with open(save_path, "w", encoding="utf-8") as f:
                    for j, segment in enumerate(segments):
                        # 更新进度
                        self.progress_var.set((segment.end / info.duration) * 100)
                        
                        # 构建 SRT 格式
                        start_str = format_timestamp(segment.start)
                        end_str = format_timestamp(segment.end)
                        
                        srt_block = f"{j + 1}\n{start_str} --> {end_str}\n{segment.text}\n\n"
                        f.write(srt_block)
                        
                        if j % 5 == 0: # 减少日志刷新频率，防止卡顿
                            self.log(f"已生成第 {j+1} 条字幕条目...")

                self.log(f"[成功] 字幕已存至: {save_path}")

            messagebox.showinfo("完成", "所有媒体文件已成功转换为 SRT 字幕！")
            
        except Exception as e:
            self.log(f"[错误] {str(e)}")
            messagebox.showerror("错误", str(e))
        finally:
            self.progress_var.set(0)
            self.status_var.set("等待中")
            self.btn_file.config(state="normal")
            self.btn_dir.config(state="normal")

if __name__ == '__main__':
    root = tk.Tk()
    app = WhisperApp(root)
    root.mainloop()
