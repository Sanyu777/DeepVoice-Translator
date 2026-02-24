import subprocess
import os
from src.config import WORK_DIR

def run_demucs(input_path):
    """人声分离"""
    print(f"🎬 正在分离人声: {input_path}")
    # 注意：-o 指向我们规范化的 WORK_DIR
    cmd = f'python -m demucs.separate -d cuda --two-stems=vocals -o "{WORK_DIR}" "{input_path}"'
    subprocess.run(cmd, shell=True, check=True)

def run_whisperx(audio_path, output_dir):
    """精准转写"""
    print(f"📝 正在转写: {audio_path}")
    cmd = f'whisperx "{audio_path}" --model large-v3 --device cuda --compute_type float16 --output_dir "{output_dir}" --output_format json'
    subprocess.run(cmd, shell=True, check=True)

def run_merge(bg_path, vocal_path, output_path):
    """最终混音"""
    print(f"🎵 正在合成最终成品...")
    # 背景音 40%，人声 120%
    filter_complex = '[0:a]volume=0.4[bg];[1:a]volume=1.2[v];[bg][v]amix=inputs=2:duration=first'
    cmd = f'ffmpeg -i "{bg_path}" -i "{vocal_path}" -filter_complex "{filter_complex}" -c:a libmp3lame -b:a 192k -y "{output_path}"'
    subprocess.run(cmd, shell=True, check=True)