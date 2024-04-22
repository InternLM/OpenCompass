from opencompass.models import HuggingFaceAboveV433Base

models = [
    dict(
        type=HuggingFaceAboveV433Base,
        abbr='CodeLlama-13b-Python',
        path='codellama/CodeLlama-13b-Python-hf',
        max_out_len=1024,
        batch_size=8,
        run_cfg=dict(num_gpus=1),
    )
]
