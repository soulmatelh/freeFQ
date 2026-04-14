import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from faster_whisper import WhisperModel

# 支持的媒体后缀
SUPPORTED_EXTENSIONS = ('.wav', '.mp3', '.m4a', '.flac', '.mp4', '.mkv', '.avi', '.mov')

class WhisperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kotoba-Whisper 深度分析转写工具")
        self.root.geometry("600x450")
        
        # --- UI 布局 ---
        self.label = tk.Label(root, text="Kotoba-Whisper 推理状态监控", font=("微软雅黑", 12, "bold"), pady=10)
        self.label.pack()

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate", variable=self.progress_var)
        self.progress.pack(pady=5)

        # 状态标签
        self.status_var = tk.StringVar(value="等待指令...")
        self.status_label = tk.Label(root, textvariable=self.status_var, fg="#2c3e50")
        self.status_label.pack()

        # 日志解读区域 (显示过程细节)
        self.log_text = tk.Text(root, height=12, width=70, state='disabled', font=("Consolas", 9))
        self.log_text.pack(pady=10, padx=10)
        
        # 按钮容器
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.btn_file = tk.Button(btn_frame, text="选择文件", command=self.select_file, width=15)
        self.btn_file.grid(row=0, column=0, padx=10)

        self.btn_dir = tk.Button(btn_frame, text="选择文件夹", command=self.select_folder, width=15)
        self.btn_dir.grid(row=0, column=1, padx=10)

    def log(self, message):
        """向界面发送解读日志"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END) # 自动滚动到底部
        self.log_text.config(state='disabled')

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("媒体文件", "*.wav *.mp3 *.mp4 *.mkv *.m4a")])
        if path:
            threading.Thread(target=self.run_task, args=(path,), daemon=True).start()

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            threading.Thread(target=self.run_task, args=(path,), daemon=True).start()

    def run_task(self, path):
        self.btn_file.config(state="disabled")
        self.btn_dir.config(state="disabled")
        self.progress_var.set(0)
        
        model_path = "./kotoba-whisper-v2.2-faster"

        try:
            self.log(">>> 阶段 1: 初始化推理引擎...")
            device = "cuda" if os.path.exists(os.path.join(os.environ.get("PROGRAMFILES", ""), "NVIDIA GPU Computing Toolkit")) else "cpu"
            self.log(f"检测到运行设备: {device.upper()}")
            
            # 载入模型
            self.status_var.set("载入模型权重中...")
            model = WhisperModel(model_path, device=device, compute_type="float32")
            self.log("模型载入完成，已加载至内存/显存。")

            # 获取文件列表
            files = [path] if os.path.isfile(path) else [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
            
            for i, file in enumerate(files):
                self.log(f"\n>>> 阶段 2: 正在解析文件 ({i+1}/{len(files)}): {os.path.basename(file)}")
                
                # 开始推理
                self.status_var.set(f"正在处理: {os.path.basename(file)}")
                segments, info = model.transcribe(file, language="ja", chunk_length=15)
                
                self.log(f"音频分析成功: 时长 {info.duration:.2f}s, 采样率 {info.sample_rate}Hz")
                self.log("正在执行 VAD (语音活动检测) 与 特征提取...")

                output_path = os.path.splitext(file)[0] + ".txt"
                with open(output_path, "w", encoding="utf-8") as f:
                    for segment in segments:
                        # 更新进度
                        p = (segment.end / info.duration) * 100
                        self.progress_var.set(p)
                        
                        # 实时解读
                        timestamp = f"{segment.start:>6.2f}s -> {segment.end:>6.2f}s"
                        self.log(f"已识别: {timestamp} | 内容: {segment.text[:20]}...")
                        
                        f.write(f"[{timestamp}] {segment.text}\n")
                
                self.log(f"--- 文件转写保存至: {os.path.basename(output_path)} ---")

            self.status_var.set("任务全部完成")
            self.log("\n[OK] 所有任务处理完毕。")
            messagebox.showinfo("完成", "转写及分析已结束。")
            
        except Exception as e:
            self.log(f"[ERROR] 发生故障: {str(e)}")
            messagebox.showerror("错误", str(e))
        finally:
            self.btn_file.config(state="normal")
            self.btn_dir.config(state="normal")

if __name__ == '__main__':
    root = tk.Tk()
    app = WhisperApp(root)
    root.mainloop()
