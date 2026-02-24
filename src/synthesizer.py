import json
import os
import asyncio
import edge_tts
from pydub import AudioSegment
from src.config import WORK_DIR, TTS_VOICE, TEMP_DIR


class AudioSynthesizer:
    def __init__(self, voice=TTS_VOICE):
        self.voice = voice
        self.concurrency_limit = 10
        self.semaphore = asyncio.Semaphore(self.concurrency_limit)

    async def _single_tts_task(self, seg, output_dir):
        """单条语音合成与时长对齐"""
        idx = seg['index']
        text = seg['chinese']
        target_duration = seg['duration']

        # 💡 明确转为字符串路径，防止 FFmpeg 命令解析出错
        temp_mp3 = str(TEMP_DIR / f"temp_{idx}.mp3")
        final_seg_path = str(output_dir / f"seg_{idx}.wav")

        async with self.semaphore:
            # 1. 网络请求合成
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(temp_mp3)

            # 💡 增加一个微小的异步等待，确保磁盘写入完成 (针对 Windows)
            await asyncio.sleep(0.1)

            # 2. 计算缩放比率
            try:
                raw_audio = AudioSegment.from_file(temp_mp3)
                actual_ms = len(raw_audio)
                speed_rate = actual_ms / (target_duration * 1000)
                safe_rate = max(0.8, min(speed_rate, 1.5))

                # 3. 使用 FFmpeg 对齐时长
                # 💡 加入 -hide_banner 减少控制台废话
                cmd = f'ffmpeg -hide_banner -i "{temp_mp3}" -filter:a "atempo={safe_rate}" -t {target_duration} -y "{final_seg_path}" -loglevel error'
                os.system(cmd)
            except Exception as e:
                print(f"❌ 片段 {idx} 处理异常: {e}")

        # 💡 在信号量外清理，减少持有锁的时间
        if os.path.exists(temp_mp3):
            try:
                os.remove(temp_mp3)
            except:
                pass  # 防止文件锁导致删除失败崩溃
        return idx

    async def synthesize(self, stem_name):
        """批量合成并拼接"""
        # ... 这里的路径逻辑正确，保持不变 ...
        input_json = WORK_DIR / "htdemucs" / stem_name / "translated_vocals.json"
        seg_dir = WORK_DIR / "htdemucs" / stem_name / "segments"
        seg_dir.mkdir(parents=True, exist_ok=True)
        final_vocal_path = WORK_DIR / "htdemucs" / stem_name / "final_chinese_vocal.wav"

        with open(input_json, 'r', encoding='utf-8') as f:
            segments = json.load(f)

        print(f"🚀 并行合成启动 (并发数: {self.concurrency_limit})，目标：{stem_name}...")
        tasks = [self._single_tts_task(seg, seg_dir) for seg in segments]
        await asyncio.gather(*tasks)

        # 💡 拼接逻辑：这里最好也加一个 try...except 保护
        combined = AudioSegment.silent(duration=0)
        current_ms = 0
        for seg in segments:
            target_start_ms = int(seg['start'] * 1000)
            seg_path = str(seg_dir / f"seg_{seg['index']}.wav")

            if not os.path.exists(seg_path):
                print(f"⚠️ 警告：片段 {seg['index']} 丢失，将填充静音")
                combined += AudioSegment.silent(duration=int(seg['duration'] * 1000))
                continue

            if target_start_ms > current_ms:
                combined += AudioSegment.silent(duration=target_start_ms - current_ms)

            combined += AudioSegment.from_file(seg_path)
            current_ms = len(combined)

        combined.export(str(final_vocal_path), format="wav")
        print(f"🎉 中文音轨合成成功: {final_vocal_path}")
        return final_vocal_path