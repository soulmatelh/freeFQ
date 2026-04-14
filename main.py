import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from faster_whisper import WhisperModel

# 定义支持的扩展名常量，方便统一维护
SUPPORTED_EXTENSIONS = ('.wav', '.mp3', '.m4a', '.flac', '.mp4', '.mkv', '.avi', '.mov')

def transcribe_audio(path, model_path):
    # 初始化设备检测逻辑
    # 如果环境中有 GPU 工具包则尝试使用 cuda，否则使用 cpu
    device = "cuda" if os.path.exists(os.path.join(os.environ.get("PROGRAMFILES", ""), "NVIDIA GPU Computing Toolkit")) else "cpu"
    
    try:
        # 建议：如果 GPU 显存小于 8G，建议将 compute_type 改为 "float16"
        model = WhisperModel(model_path, device=device, compute_type="float32")
        
        files = []
        if os.path.isfile(path):
            files.append(path)
        else:
            # 修改点：这里也需要支持视频后缀，否则选文件夹时会跳过视频
            files = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(SUPPORTED_EXTENSIONS)]

        if not files:
            messagebox.showwarning("警告", "未找到有效的媒体文件！")
            return

        for file in files:
            print(f"正在处理: {os.path.basename(file)}")
            # Kotoba-Whisper 建议参数：chunk_length=15, condition_on_previous_text=False
            segments, _ = model.transcribe(
                file, 
                language="ja", 
                beam_size=5,
                chunk_length=15, 
                condition_on_previous_text=False
            )
            
            output_path = os.path.splitext(file)[0] + ".txt"
            with open(output_path, "w", encoding="utf-8") as f:
                for segment in segments:
                    line = f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n"
                    f.write(line)
                    print(line.strip())
        
        messagebox.showinfo("成功", "转写完成！结果已保存在源文件目录。")
    except Exception as e:
        messagebox.showerror("错误", f"发生意外: {str(e)}")

def select_file():
    # 修正了缩进和文件过滤列表
    path = filedialog.askopenfilename(
        title="选择媒体文件", 
        filetypes=[
            ("所有媒体文件", "*.wav *.mp3 *.m4a *.flac *.mp4 *.mkv *.avi *.mov"),
            ("音频文件", "*.wav *.mp3 *.m4a *.flac"),
            ("视频文件", "*.mp4 *.mkv *.avi *.mov"),
            ("所有文件", "*.*")
        ]
    )
    if path:
        transcribe_audio(path, "./kotoba-whisper-v2.2-faster")

def select_folder():
    path = filedialog.askdirectory(title="选择包含媒体文件的文件夹")
    if path:
        transcribe_audio(path, "./kotoba-whisper-v2.2-faster")

# 创建 GUI 界面
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Kotoba-Whisper 转写工具 v2.2")
    root.geometry("350x250")

    label = tk.Label(root, text="Kotoba-Whisper (Faster-Whisper 版)", font=("Arial", 10, "bold"), pady=10)
    label.pack()

    desc = tk.Label(root, text="支持格式: 音频(mp3, wav...) & 视频(mp4, mkv...)", fg="gray")
    desc.pack()

    btn_file = tk.Button(root, text="选择单个文件", command=select_file, width=25, height=2)
    btn_file.pack(pady=10)

    btn_dir = tk.Button(root, text="选择文件夹批量处理", command=select_folder, width=25, height=2)
    btn_dir.pack(pady=5)

    root.mainloop()
