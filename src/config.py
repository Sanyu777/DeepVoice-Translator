# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 自动获取项目根目录 (D:\pycharmprojects\translation_mp3)
BASE_DIR = Path(__file__).resolve().parent.parent

# 规范化数据存放路径
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
WORK_DIR = DATA_DIR / "work"
OUTPUT_DIR = DATA_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"

# API 配置
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = os.getenv("DEEPSEEK_BASE_URL")
TTS_VOICE = os.getenv("TTS_VOICE", "zh-CN-XiaoxiaoNeural")

# 确保所有文件夹在运行前就存在
def init_folders():
    for folder in [INPUT_DIR, WORK_DIR, OUTPUT_DIR, TEMP_DIR]:
        folder.mkdir(parents=True, exist_ok=True)

init_folders()
if __name__ == "__main__":
    # 测试一下路径对不对
    print(f"项目根目录: {BASE_DIR}")
    init_folders()
    print("✅ 规范化文件夹已创建")