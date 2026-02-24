import json
import os
import math
from openai import OpenAI
from src.config import DEEPSEEK_KEY, DEEPSEEK_URL, WORK_DIR

class DeepSeekTranslator:
    def __init__(self):
        # 💡 不再手动填 Key，自动从 config 加载（config 又是从 .env 加载的）
        self.client = OpenAI(api_key=DEEPSEEK_KEY, base_url=DEEPSEEK_URL)

    def translate_text(self, english_text, duration_seconds):
        """单句翻译核心逻辑"""
        target_chars = max(1, math.ceil(duration_seconds * 4.5))

        system_prompt = (
            "你是一个影视配音翻译专家。请将英文翻译为地道、口语化的中文。\n"
            "【核心约束】：翻译后的中文朗读时长必须接近原视频时长。\n"
            "要求：只输出翻译结果，不要任何解释。"
        )

        user_prompt = (
            f"原文：{english_text}\n"
            f"时长：{duration_seconds:.2f} 秒\n"
            f"目标字数：请严格控制在 {target_chars} 个汉字左右。"
        )

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip().replace('"', '')
        except Exception as e:
            print(f"❌ 翻译出错: {e}")
            return ""

    def process_json(self, stem_name):
        """
        处理指定的 JSON 文件
        stem_name: 文件的纯名称，例如 'fake_face'
        """
        # 💡 路径规范化：根据文件名动态定位工作目录
        input_json = WORK_DIR / "htdemucs" / stem_name / "vocals.json"
        output_json = WORK_DIR / "htdemucs" / stem_name / "translated_vocals.json"

        if not input_json.exists():
            print(f"错误：找不到文件 {input_json}")
            return None

        with open(input_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        segments = data.get("segments", [])
        print(f"📂 成功加载 {stem_name} 的 JSON，共 {len(segments)} 个片段。")

        translated_data = []
        for i, seg in enumerate(segments):
            start = seg['start']
            end = seg['end']
            duration = end - start
            original_text = seg['text'].strip()

            print(f"正在翻译 [{i + 1}/{len(segments)}] ({duration:.2f}s)...")
            chinese_text = self.translate_text(original_text, duration)

            translated_data.append({
                "index": i,
                "start": start,
                "end": end,
                "duration": duration,
                "english": original_text,
                "chinese": chinese_text
            })

        # 保存到动态生成的路径
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 翻译完成！结果保存至: {output_json}")
        return output_json

# 方便测试
if __name__ == "__main__":
    translator = DeepSeekTranslator()
    translator.process_json("fake_face")