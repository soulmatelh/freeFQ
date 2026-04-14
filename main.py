import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from faster_whisper import WhisperModel

# --- 常量配置 ---
SUPPORTED_EXTENSIONS = ('.wav', '.mp3', '.m4a', '.flac', '.mp4', '.mkv', '.avi', '.mov')
BG_COLOR = "#f5f6fa"
PRIMARY_COLOR = "#4a90e2"
LOG_BG = "#2f3640"
LOG_FG = "#dcdde1"

def format_timestamp(seconds: float):
    td_hours = int(seconds // 3600)
    td_mins = int((seconds % 3600) // 60)
    td_secs = int(seconds % 60)
    td_msecs = int(round((seconds % 1) * 1000))
    return f"{td_hours:02}:{td_mins:02}:{td_secs:02},{td_msecs:03}"

class WhisperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kotoba-Whisper Pro 选配版")
        self.root.geometry("750x600")
        self.root.configure(bg=BG_COLOR)
        
        self.model_path = ""  # 用户选择的模型路径
        self.export_dir = ""  # 输出路径

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.setup_ui()

    def setup_ui(self):
        # 1. 标题
        header = tk.Frame(self.root, bg=PRIMARY_COLOR, height=50)
        header.pack(fill="x")
        tk.Label(header, text="KOTOBA-WHISPER 多模型工作站", fg="white", bg=PRIMARY_COLOR, font=("微软雅黑", 12, "bold")).pack(pady=10)

        # 2. 模型配置区 (新增)
        model_frame = tk.LabelFrame(self.root, text=" 1. 模型配置 ", bg=BG_COLOR, padx=10, pady=10)
        model_frame.pack(fill="x", padx=20, pady=5)
        
        self.model_var = tk.StringVar(value="请点击右侧选择本地模型文件夹...")
        tk.Label(model_frame, textvariable=self.model_var, bg=BG_COLOR, fg="red", wraplength=500).pack(side="left")
        tk.Button(model_frame, text="选择模型目录", command=self.set_model_path, bg="#9b59b6", fg="white", relief="flat").pack(side="right")

        # 3. 推荐模型参考 (只读提示)
        tips_frame = tk.Frame(self.root, bg=BG_COLOR)
        tips_frame.pack(fill="x", padx=25)
        tips_text = "推荐模型：kotoba-whisper-v2.2-faster (日语最强) | whisper-large-v3-ct2 (多语言全能)"
        tk.Label(tips_frame, text=tips_text, bg=BG_COLOR, fg="gray", font=("微软雅黑", 8)).pack(side="left")

        # 4. 输出路径
        path_frame = tk.LabelFrame(self.root, text=" 2. 保存设置 ", bg=BG_COLOR, padx=10, pady=5)
        path_frame.pack(fill="x", padx=20, pady=5)
        self.path_var = tk.StringVar(value="默认: 源文件同级目录")
        tk.Label(path_frame, textvariable=self.path_var, bg=BG_COLOR).pack(side="left")
        tk.Button(path_frame, text="更改保存位置", command=self.set_export_dir, relief="flat").pack(side="right")

        # 5. 进度与日志
        monitor_frame = tk.Frame(self.root, bg=BG_COLOR, padx=20)
        monitor_frame.pack(fill="x", pady=5)
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(monitor_frame, variable=self.progress_var, mode="determinate").pack(fill="x")
        
        self.log_text = tk.Text(self.root, bg=LOG_BG, fg=LOG_FG, font=("Consolas", 10), padx=10, pady=10)
        self.log_text.pack(fill="both", expand=True, padx=20, pady=10)

        # 6. 开始按钮
        self.btn_run = tk.Button(self.root, text=" 3. 选择媒体并开始转写 ", command=self.select_file, 
                                 bg=PRIMARY_COLOR, fg="white", font=("微软雅黑", 11, "bold"), relief="flat", state="disabled")
        self.btn_run.pack(pady=10)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()

    def set_model_path(self):
        selected = filedialog.askdirectory(title="选择包含 model.bin 的模型文件夹")
        if selected:
            # 简单检查文件夹内是否有模型文件
            if os.path.exists(os.path.join(selected, "model.bin")):
                self.model_path = selected
                self.model_var.set(f"已就绪: {os.path.basename(selected)}")
                self.btn_run.config(state="normal", bg="#2ecc71")
                self.log(f"成功识别模型目录: {selected}")
            else:
                messagebox.showerror("无效目录", "该文件夹内未发现 model.bin，请重新选择 CTranslate2 格式的模型。")

    def set_export_dir(self):
        selected = filedialog.askdirectory()
        if selected:
            self.export_dir = selected
            self.path_var.set(f"保存至: {selected}")

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("媒体文件", "*.wav *.mp3 *.mp4 *.mkv *.m4a")])
        if path:
            threading.Thread(target=self.run_task, args=(path,), daemon=True).start()

    def run_task(self, input_path):
        self.btn_run.config(state="disabled", bg="#bdc3c7")
        try:
            device = "cuda" if os.path.exists(os.path.join(os.environ.get("PROGRAMFILES", ""), "NVIDIA GPU Computing Toolkit")) else "cpu"
            self.log(f"正在加载模型至 {device.upper()}...")
            
            # 使用用户选择的路径
            model = WhisperModel(self.model_path, device=device, compute_type="float32")
            
            files = [input_path] if os.path.isfile(input_path) else [os.path.join(input_path, f) for f in os.listdir(input_path) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
            
            for i, file in enumerate(files):
                self.log(f"正在处理: {os.path.basename(file)}")
                segments, info = model.transcribe(file, language="ja", chunk_length=15)
                
                save_path = os.path.join(self.export_dir if self.export_dir else os.path.dirname(file), os.path.splitext(os.path.basename(file))[0] + ".srt")

                with open(save_path, "w", encoding="utf-8") as f:
                    for j, segment in enumerate(segments):
                        self.progress_var.set((segment.end / info.duration) * 100)
                        start, end = format_timestamp(segment.start), format_timestamp(segment.end)
                        f.write(f"{j + 1}\n{start} --> {end}\n{segment.text}\n\n")
                
                self.log(f"✅ 完成: {os.path.basename(save_path)}")

            messagebox.showinfo("成功", "转写任务已全部完成！")
        except Exception as e:
            self.log(f"❌ 错误: {str(e)}")
            messagebox.showerror("错误", str(e))
        finally:
            self.progress_var.set(0)
            self.btn_run.config(state="normal", bg="#2ecc71")

if __name__ == '__main__':
    root = tk.Tk()
    app = WhisperApp(root)
    root.mainloop()
