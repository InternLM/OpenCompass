from opencompass.models import HuggingFaceAboveV433Chat

models = [
    dict(
        type=HuggingFaceAboveV433Chat,
        abbr='CodeLlama-34b-Instruct',
        path='codellama/CodeLlama-34b-Instruct-hf',
        max_out_len=1024,
        batch_size=8,
        run_cfg=dict(num_gpus=2),
    )
]
