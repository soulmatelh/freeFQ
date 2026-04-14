def setup_ui(self):
        # 1. 顶部状态条
        header = tk.Frame(self.root, bg=PRIMARY_COLOR, height=50)
        header.pack(fill="x")
        tk.Label(header, text="KOTOBA-WHISPER 多模型推理终端", fg="white", bg=PRIMARY_COLOR, font=("微软雅黑", 12, "bold")).pack(pady=10)

        # 2. 模型选择区
        model_frame = tk.LabelFrame(self.root, text=" 1. 模型路径配置 (必要) ", bg=BG_COLOR, padx=10, pady=10)
        model_frame.pack(fill="x", padx=20, pady=5)
        
        self.model_var = tk.StringVar(value="未检测到模型，请先选择包含 model.bin 的文件夹")
        tk.Label(model_frame, textvariable=self.model_var, bg=BG_COLOR, fg="#e74c3c", wraplength=550, justify="left").pack(side="left")
        tk.Button(model_frame, text="选择模型目录", command=self.set_model_path, bg="#9b59b6", fg="white", relief="flat", padx=10).pack(side="right")

        tk.Label(self.root, text="推荐: kotoba-whisper-v2.2-faster (日语) | whisper-large-v3-ct2 (全能)", 
                 bg=BG_COLOR, fg="gray", font=("微软雅黑", 8)).pack(anchor="w", padx=25)

        # 3. 输出路径区
        path_frame = tk.LabelFrame(self.root, text=" 2. 输出位置设置 ", bg=BG_COLOR, padx=10, pady=5)
        path_frame.pack(fill="x", padx=20, pady=5)
        self.path_var = tk.StringVar(value="默认: 保存在媒体文件所在位置")
        tk.Label(path_frame, textvariable=self.path_var, bg=BG_COLOR, fg="#666").pack(side="left")
        tk.Button(path_frame, text="更改保存位置", command=self.set_export_dir, relief="flat", bg="#bdc3c7", padx=10).pack(side="right")

        # --- 重点修改：先放置底部的操作按钮，确保它们可见 ---
        # 4. 核心操作区
        btn_container = tk.Frame(self.root, bg=BG_COLOR)
        btn_container.pack(side="bottom", pady=15) # 使用 side="bottom" 强行置底

        self.btn_file = tk.Button(btn_container, text=" 选择文件并开始 ", command=lambda: self.start_task("file"), 
                                  bg=PRIMARY_COLOR, fg="white", font=("微软雅黑", 10, "bold"), 
                                  relief="flat", width=22, state="disabled", pady=8)
        self.btn_file.grid(row=0, column=0, padx=15)

        self.btn_dir = tk.Button(btn_container, text=" 选择文件夹批量转写 ", command=lambda: self.start_task("folder"), 
                                 bg=SUCCESS_COLOR, fg="white", font=("微软雅黑", 10, "bold"), 
                                 relief="flat", width=22, state="disabled", pady=8)
        self.btn_dir.grid(row=0, column=1, padx=15)

        # 5. 进度条与日志 (放在最后填充剩余空间)
        monitor_frame = tk.Frame(self.root, bg=BG_COLOR, padx=20)
        monitor_frame.pack(fill="x", side="top", pady=5)
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(monitor_frame, variable=self.progress_var, mode="determinate")
        self.progress.pack(fill="x", pady=5)
        
        self.log_text = tk.Text(self.root, bg=LOG_BG, fg=LOG_FG, font=("Consolas", 10), padx=10, pady=10, relief="flat")
        self.log_text.pack(fill="both", expand=True, padx=20, pady=5, side="top")
