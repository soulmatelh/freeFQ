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
        self.root.title("Kotoba-Whisper Pro 字幕大师")
        self.root.geometry("700x550")
        self.root.configure(bg=BG_COLOR)
        self.export_dir = ""

        # 设置全局样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TProgressbar", thickness=20, troughcolor='#dcdde1', background=PRIMARY_COLOR)

        self.setup_ui()

    def setup_ui(self):
        # 1. 标题区
        header = tk.Frame(self.root, bg=PRIMARY_COLOR, height=60)
        header.pack(fill="x")
        tk.Label(header, text="KOTOBA-WHISPER 推理工作站", fg="white", bg=PRIMARY_COLOR, 
                 font=("微软雅黑", 14, "bold"), pady=15).pack()

        # 2. 路径配置区
        path_frame = tk.LabelFrame(self.root, text=" 路径设置 ", bg=BG_COLOR, padx=10, pady=10, font=("微软雅黑", 9))
        path_frame.pack(fill="x", padx=20, pady=10)
        
        self.path_var = tk.StringVar(value="默认: 保存至媒体文件同级目录")
        tk.Label(path_frame, textvariable=self.path_var, bg=BG_COLOR, fg="#666").pack(side="left")
        tk.Button(path_frame, text="更改输出位置", command=self.set_export_dir, 
                  relief="flat", bg="#bdc3c7", padx=10).pack(side="right")

        # 3. 状态显示与进度区
        status_frame = tk.Frame(self.root, bg=BG_COLOR, padx=20)
        status_frame.pack(fill="x")
        
        self.status_var = tk.StringVar(value="等待任务开始...")
        tk.Label(status_frame, textvariable=self.status_var, bg=BG_COLOR, font=("微软雅黑", 10)).pack(anchor="w")
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(status_frame, mode="determinate", variable=self.progress_var, style="TProgressbar")
        self.progress.pack(fill="x", pady=5)

        # 4. 日志解读区 (重点美化)
        log_frame = tk.LabelFrame(self.root, text=" 推理深度解读 ", bg=BG_COLOR, padx=5, pady=5, font=("微软雅黑", 9))
        log_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.log_text = tk.Text(log_frame, bg=LOG_BG, fg=LOG_FG, font=("Consolas", 10), 
                                relief="flat", padx=10, pady=10)
        self.log_text.pack(fill="both", expand=True)
        # 添加滚动条
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

        # 5. 操作按钮区
        btn_frame = tk.Frame(self.root, bg=BG_COLOR, pady=15)
        btn_frame.pack()

        self.btn_file = tk.Button(btn_frame, text=" 选择文件开始 ", command=self.select_file, 
                                  bg=PRIMARY_COLOR, fg="white", font=("微软雅黑", 10, "bold"), 
                                  relief="flat", width=20, pady=8)
        self.btn_file.grid(row=0, column=0, padx=10)

        self.btn_dir = tk.Button(btn_frame, text=" 批量处理文件夹 ", command=self.select_folder, 
                                 bg="#2ecc71", fg="white", font=("微软雅黑", 10, "bold"), 
                                 relief="flat", width=20, pady=8)
        self.btn_dir.grid(row=0, column=1, padx=10)

    def log(self, message, tag=None):
        self.log_text.config(state='normal')
        curr_time = time.strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{curr_time}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()

    def set_export_dir(self):
        selected = filedialog.askdirectory()
        if selected:
            self.export_dir = selected
            self.path_var.set(f"保存至: {selected}")
            self.log(f"📍 输出目录已切换: {selected}")

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("媒体文件", "*.wav *.mp3 *.mp4 *.mkv *.m4a")])
        if path:
            threading.Thread(target=self.run_task, args=(path,), daemon=True).start()

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            threading.Thread(target=self.run_task, args=(path,), daemon=True).start()

    def run_task(self, input_path):
        self.btn_file.config(state="disabled", bg="#bdc3c7")
        self.btn_dir.config(state="disabled", bg="#bdc3c7")
        
        model_path = "./kotoba-whisper-v2.2-faster"

        try:
            self.log("🚀 正在初始化 Kotoba-Whisper v2.2 引擎...")
            # 设备检测
            device = "cuda" if os.path.exists(os.path.join(os.environ.get("PROGRAMFILES", ""), "NVIDIA GPU Computing Toolkit")) else "cpu"
            self.log(f"⚙️ 运行算力检测: {device.upper()} 模式")
            
            # 载入模型 (此处加载时间较长)
            self.status_var.set("正在从存储载入模型权重...")
            model = WhisperModel(model_path, device=device, compute_type="float32")
            self.log("✅ 模型加载成功。")

            # 筛选文件
            files = [input_path] if os.path.isfile(input_path) else [os.path.join(input_path, f) for f in os.listdir(input_path) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
            
            for i, file in enumerate(files):
                file_name = os.path.basename(file)
                self.log(f"🔍 正在解析音频流: {file_name}")
                self.status_var.set(f"正在转写 ({i+1}/{len(files)}): {file_name}")
                
                # 开始推理 - 修复 sample_rate 错误
                segments, info = model.transcribe(file, language="ja", chunk_length=15, beam_size=5)
                self.log(f"📈 音频解析完成: 总时长 {info.duration:.2f}s")
                self.log("🧠 神经网络解码中...")

                # 确定保存路径
                base_name = os.path.splitext(file_name)[0] + ".srt"
                save_path = os.path.join(self.export_dir if self.export_dir else os.path.dirname(file), base_name)

                with open(save_path, "w", encoding="utf-8") as f:
                    for j, segment in enumerate(segments):
                        # 实时更新进度条
                        self.progress_var.set((segment.end / info.duration) * 100)
                        
                        # 写入 SRT
                        start_str = format_timestamp(segment.start)
                        end_str = format_timestamp(segment.end)
                        f.write(f"{j + 1}\n{start_str} --> {end_str}\n{segment.text}\n\n")
                        
                        # 日志抽样显示
                        if j % 5 == 0:
                            self.log(f"已生成字幕: {start_str} -> {segment.text[:15]}...")

                self.log(f"⭐ 成功! 字幕已保存至: {os.path.basename(save_path)}")

            messagebox.showinfo("任务完成", "所有的 SRT 字幕已生成完毕！")
            
        except Exception as e:
            self.log(f"❌ 发生致命错误: {str(e)}")
            messagebox.showerror("错误", str(e))
        finally:
            self.progress_var.set(0)
            self.status_var.set("准备就绪")
            self.btn_file.config(state="normal", bg=PRIMARY_COLOR)
            self.btn_dir.config(state="normal", bg="#2ecc71")

if __name__ == '__main__':
    root = tk.Tk()
    # 尝试设置程序图标 (如果以后你有 .ico 文件)
    # root.iconbitmap('logo.ico')
    app = WhisperApp(root)
    root.mainloop()
