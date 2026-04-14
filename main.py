import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from faster_whisper import WhisperModel

# --- 常量与样式配置 ---
SUPPORTED_EXTENSIONS = ('.wav', '.mp3', '.m4a', '.flac', '.mp4', '.mkv', '.avi', '.mov')
BG_COLOR = "#f5f6fa"
PRIMARY_COLOR = "#4a90e2"
SUCCESS_COLOR = "#2ecc71"
LOG_BG = "#2f3640"
LOG_FG = "#dcdde1"

def format_timestamp(seconds: float):
    """SRT 时间格式化 HH:MM:SS,mmm"""
    td_hours = int(seconds // 3600)
    td_mins = int((seconds % 3600) // 60)
    td_secs = int(seconds % 60)
    td_msecs = int(round((seconds % 1) * 1000))
    return f"{td_hours:02}:{td_mins:02}:{td_secs:02},{td_msecs:03}"

class WhisperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kotoba-Whisper Pro 工作站")
        self.root.geometry("750x700")
        self.root.configure(bg=BG_COLOR)
        
        self.model_path = ""
        self.export_dir = ""

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.setup_ui()

    def setup_ui(self):
        # ---------------------------------------------------------
        # 采用纯粹的自上而下 (Top-to-Bottom) 布局，杜绝渲染重叠 Bug
        # ---------------------------------------------------------

        # 1. 顶部状态条
        header = tk.Frame(self.root, bg=PRIMARY_COLOR, height=50)
        header.pack(side="top", fill="x")
        tk.Label(header, text="FASTR-WHISPER 多模型推理终端", fg="white", bg=PRIMARY_COLOR, font=("微软雅黑", 12, "bold")).pack(pady=10)

        # 2. 模型选择区
        model_frame = tk.LabelFrame(self.root, text=" 1. 模型路径配置 (必要) ", bg=BG_COLOR, padx=10, pady=10)
        model_frame.pack(side="top", fill="x", padx=20, pady=10)
        
        self.model_var = tk.StringVar(value="未检测到模型，请先选择包含 model.bin 的文件夹")
        tk.Label(model_frame, textvariable=self.model_var, bg=BG_COLOR, fg="#e74c3c", wraplength=500, justify="left").pack(side="left")
        tk.Button(model_frame, text="选择模型目录", command=self.set_model_path, bg="#9b59b6", fg="white", relief="flat", padx=10).pack(side="right")

        # 3. 核心操作区 (移动到了模型选择的正下方)
        action_frame = tk.LabelFrame(self.root, text=" 2. 开始任务 ", bg=BG_COLOR, padx=10, pady=10)
        action_frame.pack(side="top", fill="x", padx=20, pady=5)

        btn_container = tk.Frame(action_frame, bg=BG_COLOR)
        btn_container.pack()

        self.btn_file = tk.Button(btn_container, text=" 选择单个文件并转写 ", command=lambda: self.start_task("file"), 
                                  bg=PRIMARY_COLOR, fg="white", font=("微软雅黑", 10, "bold"), 
                                  relief="flat", width=22, state="disabled", pady=8)
        self.btn_file.grid(row=0, column=0, padx=15)

        self.btn_dir = tk.Button(btn_container, text=" 选择文件夹批量转写 ", command=lambda: self.start_task("folder"), 
                                 bg=SUCCESS_COLOR, fg="white", font=("微软雅黑", 10, "bold"), 
                                 relief="flat", width=22, state="disabled", pady=8)
        self.btn_dir.grid(row=0, column=1, padx=15)

        # 4. 输出路径区
        path_frame = tk.LabelFrame(self.root, text=" 3. 输出位置设置 (可选) ", bg=BG_COLOR, padx=10, pady=5)
        path_frame.pack(side="top", fill="x", padx=20, pady=10)
        
        self.path_var = tk.StringVar(value="默认: 保存在媒体文件所在位置")
        tk.Label(path_frame, textvariable=self.path_var, bg=BG_COLOR, fg="#666").pack(side="left")
        tk.Button(path_frame, text="更改保存位置", command=self.set_export_dir, relief="flat", bg="#bdc3c7", padx=10).pack(side="right")

        # 5. 进度条与日志区 (填满底部剩余空间)
        monitor_frame = tk.LabelFrame(self.root, text=" 运行日志与进度 ", bg=BG_COLOR, padx=10, pady=5)
        monitor_frame.pack(side="top", fill="both", expand=True, padx=20, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(monitor_frame, variable=self.progress_var, mode="determinate")
        self.progress.pack(fill="x", pady=5)
        
        self.log_text = tk.Text(monitor_frame, bg=LOG_BG, fg=LOG_FG, font=("Consolas", 10), padx=10, pady=10, relief="flat")
        self.log_text.pack(fill="both", expand=True)

    # --- 核心逻辑 ---
    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()

    def set_model_path(self):
        selected = filedialog.askdirectory(title="选择 CTranslate2 模型文件夹")
        if selected:
            if os.path.exists(os.path.join(selected, "model.bin")):
                self.model_path = selected
                self.model_var.set(f"模型就绪: {os.path.basename(selected)}")
                self.log(f"成功加载模型配置: {selected}")
                # 激活转写按钮，同时变色以提示用户可点击
                self.btn_file.config(state="normal", bg=PRIMARY_COLOR)
                self.btn_dir.config(state="normal", bg=SUCCESS_COLOR)
            else:
                messagebox.showerror("模型无效", "所选目录内未找到 model.bin，请确保是已转换的模型格式。")

    def set_export_dir(self):
        selected = filedialog.askdirectory()
        if selected:
            self.export_dir = selected
            self.path_var.set(f"保存至: {selected}")
            self.log(f"已设置输出目录: {selected}")

    def start_task(self, mode):
        if mode == "file":
            path = filedialog.askopenfilename(filetypes=[("媒体文件", "*.wav *.mp3 *.mp4 *.mkv *.m4a *.flac")])
        else:
            path = filedialog.askdirectory()
        
        if path:
            threading.Thread(target=self.run_process, args=(path,), daemon=True).start()

    def run_process(self, path):
        # 任务开始，禁用按钮变灰
        self.btn_file.config(state="disabled", bg="#bdc3c7")
        self.btn_dir.config(state="disabled", bg="#bdc3c7")
        
        try:
            device = "cuda" if os.path.exists(os.path.join(os.environ.get("PROGRAMFILES", ""), "NVIDIA GPU Computing Toolkit")) else "cpu"
            self.log(f"🚀 初始化引擎 (设备: {device.upper()})...")
            
            # 加载模型
            model = WhisperModel(self.model_path, device=device, compute_type="float32")
            
            # 扫描文件列表
            files = [path] if os.path.isfile(path) else [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
            
            if not files:
                self.log("⚠ 未发现支持的媒体文件。")
                return

            for i, file in enumerate(files):
                f_name = os.path.basename(file)
                self.log(f"读取文件 ({i+1}/{len(files)}): {f_name}")
                
                # 开始推理
                segments, info = model.transcribe(file, language="ja", chunk_length=15, beam_size=5)
                self.log(f"正在进行神经网络解码，音频时长: {info.duration:.2f}s")

                # 构造保存路径
                save_name = os.path.splitext(f_name)[0] + ".srt"
                save_path = os.path.join(self.export_dir if self.export_dir else os.path.dirname(file), save_name)

                # 写入字幕并更新进度
                with open(save_path, "w", encoding="utf-8") as f:
                    for j, segment in enumerate(segments):
                        self.progress_var.set((segment.end / info.duration) * 100)
                        start, end = format_timestamp(segment.start), format_timestamp(segment.end)
                        f.write(f"{j + 1}\n{start} --> {end}\n{segment.text}\n\n")

                self.log(f"✅ 转写成功: {save_name}")

            messagebox.showinfo("任务完成", "所有的媒体文件已处理完毕！")
        except Exception as e:
            self.log(f"❌ 运行报错: {str(e)}")
            messagebox.showerror("运行时错误", str(e))
        finally:
            # 任务结束，恢复颜色和点击状态
            self.progress_var.set(0)
            self.btn_file.config(state="normal", bg=PRIMARY_COLOR)
            self.btn_dir.config(state="normal", bg=SUCCESS_COLOR)

if __name__ == '__main__':
    root = tk.Tk()
    app = WhisperApp(root)
    root.mainloop()
