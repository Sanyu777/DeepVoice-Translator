import warnings
import os
warnings.filterwarnings("ignore", category=UserWarning)
os.environ["PYTHONWARNINGS"] = "ignore"

import shutil
from src.config import TEMP_DIR
import sys
import asyncio
from pathlib import Path
from src.config import INPUT_DIR, WORK_DIR, OUTPUT_DIR
from src.processor import run_demucs, run_whisperx, run_merge
from src.translator import DeepSeekTranslator
from src.synthesizer import AudioSynthesizer
import torch
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

async def main(file_name):
    input_path = INPUT_DIR / file_name
    stem_name = input_path.stem

    # 路径定义
    current_work_dir = WORK_DIR / "htdemucs" / stem_name
    vocals_path = current_work_dir / "vocals.wav"
    bg_path = current_work_dir / "no_vocals.wav"
    final_output = OUTPUT_DIR / f"{stem_name}_CN.mp3"

    # 1. 分离
    run_demucs(input_path)

    # 2. 转写
    run_whisperx(vocals_path, current_work_dir)

    # 3. 翻译
    translator = DeepSeekTranslator()
    translator.process_json(stem_name)

    # 4. 合成
    synthesizer = AudioSynthesizer()
    await synthesizer.synthesize(stem_name)

    # 5. 混音
    vocal_cn = current_work_dir / "final_chinese_vocal.wav"
    run_merge(bg_path, vocal_cn, final_output)

    # 6. 任务完成后清理 temp 文件夹
    if TEMP_DIR.exists():
        # 清理该文件夹下的所有内容，但保留文件夹本身
        for file in TEMP_DIR.glob("*"):
            try:
                if file.is_file():
                    file.unlink()
            except Exception as e:
                print(f"清理临时文件失败: {e}")

    print(f"\n✨✨✨ 任务圆满完成！成品就在: {final_output}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用说明: python main.py <文件名>\n示例: python main.py fake_face.mp3")
    else:
        asyncio.run(main(sys.argv[1]))