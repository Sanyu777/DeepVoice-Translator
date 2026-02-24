# 🎙️ DeepVoice-Translator: 工业级视频/音频翻译配音流水线

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**DeepVoice-Translator** 是一款基于深度学习的自动化媒体翻译工具。它不仅能翻译文字，更能实现从 **人声分离 -> 精准转写 -> 语义对齐翻译 -> 高清配音合成 -> 自动混音** 的全链路闭环，生成语速自然、音质纯净的译制成品。



---

## ✨ 核心特性

* **🎙️ 人声/背景音分离 (Demucs)**：采用 Facebook 的 Hybrid Transformer 模型，从复杂 BGM 中提取纯净人声，确保配音不受原音干扰。
* **⏱️ 毫秒级转写对齐 (WhisperX)**：通过 Alignment Model 锁定单词精确时间戳，实现翻译后的“音画同步”。
* **🤖 等长语义翻译 (DeepSeek)**：基于 LLM 的智能 Prompt，根据原片时长自动调整翻译长度，告别配音过快。
* **⚡ 异步并行合成 (Edge-TTS)**：利用异步技术，配音合成速度提升 5-10 倍，并支持语速动态缩放。
* **🖥️ 现代化交互界面**：提供基于 Gradio 的 Web UI，支持实时进度查看、文件预览及一键处理。

---

## 🛠️ 环境准备与安装 (核心优势)

为了避免深度学习库（如 PyTorch）与不同显卡驱动之间的版本冲突，本项目提供了一个 **智能环境配置脚本**。

### 1. 软件依赖
* **Python 3.12+**
* **FFmpeg**: **必须项**。请确保其已加入系统环境变量 `PATH`。

### 2. 自动化安装 (推荐 ⭐️)
本项目推荐使用 `uv` 进行高效包管理：

```powershell
# 1. 克隆仓库
git clone [https://github.com/Sanyu777/DeepVoice-Translator.git](https://github.com/Sanyu777/DeepVoice-Translator.git)
cd DeepVoice-Translator

# 2. 创建环境 (建议使用 uv)
uv venv --seed --python 3.12
.\.venv\Scripts\activate

# 3. 运行智能安装脚本 (自动识别 GPU 并补齐依赖)
python install.py

```

---

## ⚙️ 配置文件

将根目录下的 `.env.example` 重命名为 `.env`，并填入您的 API 信息：

```env
# DeepSeek API 配置
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=[https://api.deepseek.com/v1](https://api.deepseek.com/v1)

# TTS 偏好
TTS_VOICE=zh-CN-XiaoxiaoNeural

```

---

## 🚀 快速使用

### 方式一：网页界面模式 (GUI)

最直观的使用方式，支持文件拖拽。

```powershell
python gui.py

```

访问：`http://127.0.0.1:7860`

### 方式二：命令行模式 (CLI)

适合批量处理。

```powershell
python main.py "your_video.mp4"

```

---

## 📂 项目结构说明

```text
DeepVoice-Translator/
├── src/                # 核心逻辑 (分离、转写、翻译、合成)
├── data/               # 数据存储 (input, work, output)
├── libs/               # 本地维护的 WhisperX & Demucs 源码
├── install.py          # 智能硬件自适应安装脚本
├── gui.py              # Gradio 界面程序
└── .env                # 私密配置

```

---

## ⚠️ 常见问题

1. **显存报错**：如果运行中提示显存不足，请在 `src/config.py` 中尝试减小 `batch_size`。
2. **模型下载**：首次运行会从 HuggingFace/GitHub 下载约 2GB 的模型权重，请确保网络通畅。

---

## 🤝 鸣谢

本项目整合了以下优秀开源库：

* [Demucs](https://github.com/facebookresearch/demucs)
* [WhisperX](https://github.com/m-bain/whisperX)
* [Edge-TTS](https://github.com/rany2/edge-tts)

```
