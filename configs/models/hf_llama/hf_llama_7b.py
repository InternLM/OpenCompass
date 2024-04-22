from opencompass.models import HuggingFaceCausalLM

models = [
    # LLaMA 7B
    dict(
        type=HuggingFaceCausalLM,
        tokenizer_path='huggyllama/llama-7b',
        tokenizer_kwargs=dict(padding_side='left',
                              truncation_side='left',
                              use_fast=False,
                              ),
        max_out_len=100,
        max_seq_len=2048,
        batch_size=8,
        model_kwargs=dict(device_map='auto'),
        batch_padding=False, # if false, inference with for-loop without batch padding
        run_cfg=dict(num_gpus=1, num_procs=1),
    )
]


from opencompass.models import HuggingFaceAboveV433Base

models = [
    dict(
        type=HuggingFaceAboveV433Base,
        abbr='llama-7b-hf',
        path='huggyllama/llama-7b',
        max_out_len=1024,
        batch_size=8,
        run_cfg=dict(num_gpus=1),
    )
]
