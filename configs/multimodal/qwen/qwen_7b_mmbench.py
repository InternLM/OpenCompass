# from opencompass.multimodal.models.visualglm import (VisualGLMBasePostProcessor, VisualGLMMMBenchPromptConstructor)
from opencompass.multimodal.models.qwen import QwenMMBenchPromptConstructor

# dataloader settings
val_pipeline = [
    dict(type='mmpretrain.torchvision/Resize',
         size=(448, 448),
         interpolation=3),
    dict(type='mmpretrain.torchvision/ToTensor'),
    dict(type='mmpretrain.torchvision/Normalize',
         mean=(0.48145466, 0.4578275, 0.40821073),
         std=(0.26862954, 0.26130258, 0.27577711)),
    dict(type='mmpretrain.PackInputs',
         algorithm_keys=[
             'question', 'options', 'category', 'l2-category', 'context',
             'index', 'options_dict'
         ])
]

dataset = dict(type='opencompass.MMBenchDataset',
               data_file='data/mmbench/mmbench_test_20230712.tsv',
               pipeline=val_pipeline)

qwen_mmbench_dataloader = dict(batch_size=1,
                  num_workers=4,
                  dataset=dataset,
                  collate_fn=dict(type='pseudo_collate'),
                  sampler=dict(type='DefaultSampler', shuffle=False))

# model settings
qwen_model = dict(
    type='qwen',
    pretrained_path='Qwen/Qwen-VL',  # or Huggingface repo id
    prompt_constructor=dict(type=QwenMMBenchPromptConstructor),
    post_processor=dict()
)

# evaluation settings
qwen_mmbench_evaluator = [
    dict(type='opencompass.DumpResults',
         save_path='work_dirs/qwen-7b-mmbench.xlsx')
]
