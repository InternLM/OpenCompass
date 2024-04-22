from opencompass.models import HuggingFaceAboveV433Chat

models = [
    dict(
        type=HuggingFaceAboveV433Chat,
        abbr='mistral-7b-instruct-v0.2-hf',
        path='mistralai/Mistral-7B-Instruct-v0.2',
        max_out_len=1024,
        batch_size=8,
        run_cfg=dict(num_gpus=1),
    )
]
