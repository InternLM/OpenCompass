from opencompass.models import HuggingFaceAboveV433Chat

models = [
    dict(
        type=HuggingFaceAboveV433Chat,
        abbr='internlm2-chat-math-20b-hf',
        path='internlm/internlm2-math-20b',
        max_out_len=1024,
        batch_size=8,
        run_cfg=dict(num_gpus=2),
        generation_kwargs = {"eos_token_id": [2, 92542]},
    )
]
