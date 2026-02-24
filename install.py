import subprocess
import platform
import sys
import os

def run_pip(args):
    """使用当前环境的 Python 运行 pip"""
    cmd = [sys.executable, "-m", "pip", "install"] + args
    print(f"执行: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e}")
        raise

def setup():
    print("🚀 开始 DeepVoice-Translator 智能环境配置...")

    # 0. 确保 pip 是最新的
    print("🔄 正在升级 pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

    # 1. 安装基础依赖
    print("📦 正在安装基础依赖 (补齐所有 Demucs/WhisperX 隐藏依赖)...")
    base_deps = [
        "openai>=1.0.0", "edge-tts", "pydub", "python-dotenv", "gradio",
        "huggingface-hub<1.0", "transformers", "librosa", "soundfile",
        "scipy", "tqdm", "scikit-learn", "pandas", "numpy", "nltk",
        "dora-search", "diffq", "lameenc", "omegaconf", "julius",
        "treetable", "einops", "openunmix", "pyyaml",
        "av", "ffmpeg-python",
        "faster-whisper", "tensorboard",
        # 💡 补齐 WhisperX 必需的语音活动检测库
        "pyannote.audio"
    ]
    run_pip(base_deps)

    # 2. 硬件侦测与 Torch 安装
    system = platform.system()
    has_gpu = False
    try:
        subprocess.check_output("nvidia-smi", shell=True, stderr=subprocess.STDOUT)
        has_gpu = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        has_gpu = False

    if has_gpu:
        print("✅ 检测到 NVIDIA GPU！安装 CUDA 加速版 PyTorch (cu121)...")
        run_pip([
            "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cu121",
            "--force-reinstall"
        ])
    elif system == "Darwin":
        print("🍎 检测到 macOS，安装原生加速版 PyTorch...")
        run_pip(["torch", "torchvision", "torchaudio", "--force-reinstall"])
    else:
        print("💻 未检测到适配 GPU，安装 CPU 稳定版...")
        run_pip([
            "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cpu",
            "--force-reinstall"
        ])

    # 3. 安装本地库 (Editable 模式)
    print("🛠️ 正在关联本地核心库 (whisperX & demucs)...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    whisperx_path = os.path.join(current_dir, "libs", "whisperX")
    demucs_path = os.path.join(current_dir, "libs", "demucs_src")

    if os.path.exists(whisperx_path) and os.path.exists(demucs_path):
        run_pip(["-e", whisperx_path, "--no-deps"])
        run_pip(["-e", demucs_path, "--no-deps"])
    else:
        print("❌ 错误: 找不到 libs 文件夹下的源码。")
        sys.exit(1)

    print("\n✨ 环境配置完成！")
    print("💡 现在请输入: python gui.py 启动项目。")

if __name__ == "__main__":
    try:
        setup()
    except Exception as e:
        print(f"\n❌ 安装过程中出现严重错误: {e}")
        sys.exit(1)