import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from faster_whisper import WhisperModel

def transcribe_audio(path, model_path):
    # 初始化模型
    # 注意：打包成EXE后，建议默认使用 CPU 或自动检测，否则在没有显卡的机器上会崩溃
    device = "cuda" if os.path.exists(os.path.join(os.environ.get("PROGRAMFILES", ""), "NVIDIA GPU Computing Toolkit")) else "cpu"
    
    try:
        model = WhisperModel(model_path, device=device, compute_type="float32")
        
        # 判断是单个文件还是文件夹
        files = []
        if os.path.isfile(path):
            files.append(path)
        else:
            files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('.wav', '.mp3', '.m4a', '.flac'))]

        if not files:
            messagebox.showwarning("警告", "未找到有效的音频文件！")
            return

        for file in files:
            print(f"正在处理: {os.path.basename(file)}")
            segments, _ = model.transcribe(file, language="ja", beam_size=5)
            
            # 结果保存为同名的 .txt 文件
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
    path = filedialog.askopenfilename(title="选择音频文件", filetypes=[("Audio Files", "*.wav *.mp3 *.m4a *.flac")])
    if path:
        transcribe_audio(path, "./kotoba-whisper-v2.2-faster")

def select_folder():
    path = filedialog.askdirectory(title="选择包含音频的文件夹")
    if path:
        transcribe_audio(path, "./kotoba-whisper-v2.2-faster")

# 创建简单的GUI界面
root = tk.Tk()
root.title("Kotoba-Whisper 转写工具")
root.geometry("300x200")

label = tk.Label(root, text="请选择处理模式", pady=20)
label.pack()

btn_file = tk.Button(root, text="选择单个文件", command=select_file, width=20)
btn_file.pack(pady=5)

btn_dir = tk.Button(root, text="选择文件夹", command=select_folder, width=20)
btn_dir.pack(pady=5)

root.mainloop()
