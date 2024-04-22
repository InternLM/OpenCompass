from opencompass.models import HuggingFaceAboveV433Chat

models = [
    dict(
        type=HuggingFaceAboveV433Chat,
        abbr='qwen-1.8b-chat-hf',
        path='Qwen/Qwen-1_8B-Chat',
        max_out_len=1024,
        batch_size=8,
        run_cfg=dict(num_gpus=1),
    )
]
