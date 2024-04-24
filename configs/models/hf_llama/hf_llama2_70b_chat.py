from opencompass.models import HuggingFaceCausalLM

_meta_template = dict(
    round=[
        dict(role="HUMAN", begin='[INST] ', end=' [/INST]'),
        dict(role="BOT", begin=' ', end=' ', generate=True),
    ],
)

models = [
    dict(
        type=HuggingFaceCausalLM,
        abbr='llama-2-70b-chat-hf',
        path="meta-llama/Llama-2-70b-chat-hf",
        tokenizer_path='meta-llama/Llama-2-70b-chat-hf',
        model_kwargs=dict(
            device_map='auto'
        ),
        tokenizer_kwargs=dict(
            padding_side='left',
            truncation_side='left',
            use_fast=False,
        ),
        meta_template=_meta_template,
        max_out_len=100,
        max_seq_len=2048,
        batch_size=8,
        run_cfg=dict(num_gpus=4, num_procs=1),
        end_str='[INST]',
        batch_padding=True,
    )
]
