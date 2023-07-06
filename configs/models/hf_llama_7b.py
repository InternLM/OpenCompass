from opencompass.models import HuggingFaceCausalLM


models = [
    # LLaMA 7B
    dict(
        type=HuggingFaceCausalLM,
        abbr='llama-7b-hf',
        path="decapoda-research/llama-7b-hf",
        tokenizer_path='decapoda-research/llama-7b-hf',
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
