import gradio as gr
import asyncio
import os
import shutil
from pathlib import Path
from main import main as run_pipeline  # 引用你 main.py 里的核心逻辑
from src.config import INPUT_DIR, OUTPUT_DIR, init_folders

# 初始化文件夹
init_folders()


async def process_video_gui(input_file):
    """Gradio 调用的包装函数"""
    if input_file is None:
        yield "❌ 请先上传文件！", None
        return  # 💡 结束函数，不带返回值

    try:
        # 1. 获取上传文件的路径和名称
        # input_file 在 Gradio 中可能是一个文件对象或字典，视版本而定
        file_path = input_file.name if hasattr(input_file, 'name') else input_file
        original_path = Path(file_path)
        file_name = original_path.name

        # 2. 将上传的文件复制到项目的 data/input 目录中
        target_input_path = INPUT_DIR / file_name
        shutil.copy(str(original_path), str(target_input_path))

        yield f"🚀 文件已就绪，开始处理：{file_name}...", None

        # 3. 运行主流水线
        await run_pipeline(file_name)

        # 4. 找到输出文件
        stem_name = target_input_path.stem
        final_output = OUTPUT_DIR / f"{stem_name}_CN.mp3"

        if final_output.exists():
            yield "✨ 处理完成！点击下方播放或下载。", str(final_output)
        else:
            yield "❌ 混音失败，未找到生成文件。", None

    except Exception as e:
        yield f"💥 运行出错: {str(e)}", None
        return

# --- 构建 Gradio 界面 ---
with gr.Blocks(title="AI 视频翻译配音助手") as demo:
    gr.Markdown("""
    # 🎙️ AI 视频/音频翻译配音助手
    上传你的英文视频或音频，AI 将自动进行：人声分离 -> 语音转写 -> DeepSeek 翻译 -> 中文配音 -> 自动混音。
    """)

    with gr.Row():
        with gr.Column():
            input_file = gr.File(label="上传视频或音频 (mp4/mp3)", file_types=[".mp4", ".mp3"])
            btn = gr.Button("开始自动化翻译", variant="primary")

        with gr.Column():
            status_output = gr.Textbox(label="运行状态", placeholder="等待任务开始...", interactive=False)
            audio_output = gr.Audio(label="中文配音成品", type="filepath")

    # 点击按钮触发异步函数
    # 使用 yield 模式可以实现状态实时更新
    btn.click(
        fn=process_video_gui,
        inputs=[input_file],
        outputs=[status_output, audio_output]
    )

    gr.Markdown("--- \n *提示：由于需要调用 GPU，处理时长约为视频长度的 1/2。*")

if __name__ == "__main__":
    # 启动本地服务器
    demo.queue().launch(inbrowser=True)