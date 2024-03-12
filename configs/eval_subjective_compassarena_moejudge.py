from os import getenv as gv
from opencompass.models import HuggingFaceCausalLM
from mmengine.config import read_base

with read_base():
    from .datasets.subjective.compassarena.compassarena_compare_moe import subjective_datasets

from opencompass.models import HuggingFaceCausalLM, HuggingFace, HuggingFaceChatGLM3, OpenAI
from opencompass.models.openai_api import OpenAIAllesAPIN
from opencompass.partitioners import NaivePartitioner, SizePartitioner
from opencompass.partitioners.sub_naive import SubjectiveNaivePartitioner
from opencompass.partitioners.sub_size import SubjectiveSizePartitioner
from opencompass.runners import LocalRunner
from opencompass.runners import SlurmSequentialRunner
from opencompass.tasks import OpenICLInferTask
from opencompass.tasks.subjective_eval import SubjectiveEvalTask
from opencompass.summarizers import CompassArenaSummarizer

api_meta_template = dict(
    round=[
        dict(role='HUMAN', api_role='HUMAN'),
        dict(role='BOT', api_role='BOT', generate=True),
    ],
    reserved_roles=[dict(role='SYSTEM', api_role='SYSTEM')],
)

# -------------Inference Stage ----------------------------------------
chatglm3 =     dict(
        type=HuggingFaceChatGLM3,
        abbr='chatglm3-6b-32k-hf',
        path='THUDM/chatglm3-6b',
        tokenizer_path='THUDM/chatglm3-6b',
        model_kwargs=dict(
            device_map='auto',
            trust_remote_code=True,
        ),
        tokenizer_kwargs=dict(
            padding_side='left',
            truncation_side='left',
            trust_remote_code=True,
        ),
        generation_kwargs=dict(
            do_sample=True,
        ),
        meta_template=api_meta_template,
        max_out_len=2048,
        max_seq_len=4096,
        batch_size=1,
        run_cfg=dict(num_gpus=1, num_procs=1),
    )
qwen =     dict(
        type=HuggingFaceChatGLM3,
        abbr='qwen',
        path='THUDM/chatglm3-6b',
        tokenizer_path='THUDM/chatglm3-6b',
        model_kwargs=dict(
            device_map='auto',
            trust_remote_code=True,
        ),
        tokenizer_kwargs=dict(
            padding_side='left',
            truncation_side='left',
            trust_remote_code=True,
        ),
        generation_kwargs=dict(
            do_sample=True,
        ),
        meta_template=api_meta_template,
        max_out_len=2048,
        max_seq_len=4096,
        batch_size=1,
        run_cfg=dict(num_gpus=1, num_procs=1),
    )
baichuan =     dict(
        type=HuggingFaceChatGLM3,
        abbr='baichuan',
        path='THUDM/chatglm3-6b',
        tokenizer_path='THUDM/chatglm3-6b',
        model_kwargs=dict(
            device_map='auto',
            trust_remote_code=True,
        ),
        tokenizer_kwargs=dict(
            padding_side='left',
            truncation_side='left',
            trust_remote_code=True,
        ),
        generation_kwargs=dict(
            do_sample=True,
        ),
        meta_template=api_meta_template,
        max_out_len=2048,
        max_seq_len=4096,
        batch_size=1,
        run_cfg=dict(num_gpus=1, num_procs=1),
    )
# For subjective evaluation, we often set do sample for models
models = [chatglm3,qwen,baichuan
]

datasets = [*subjective_datasets]

gpt4 = dict(
    abbr='gpt4-turbo',
    type=OpenAI,
    path='gpt-4-1106-preview',
    key='',  # The key will be obtained from $OPENAI_API_KEY, but you can write down your key here as well
    meta_template=api_meta_template,
    query_per_second=1,
    max_out_len=2048,
    max_seq_len=4096,
    batch_size=4,
    retry=20,
    temperature=1,
)  # Re-inference gpt4's predictions or you can choose to use the pre-commited gpt4's predictions

infer = dict(
    partitioner=dict(type=SizePartitioner,  max_task_size=200),
    runner=dict(
        type=SlurmSequentialRunner,
        partition='llm_dev2',
        quotatype='auto',
        max_num_workers=256,
        task=dict(type=OpenICLInferTask),
    ),
)

# -------------Evalation Stage ----------------------------------------

## ------------- JudgeLLM Configuration
judge_models = [chatglm3,baichuan,qwen]

## ------------- Evaluation Configuration
eval = dict(
    partitioner=dict(
        type=SubjectiveSizePartitioner,
        #strategy='split',
        max_task_size=300,
        mode='m2n',
        base_models=[baichuan],
        compare_models=models,
        judge_models=judge_models,
        meta_judge_model=qwen,
        infer_order='random'
    ),
    runner=dict(
        type=SlurmSequentialRunner,
        partition='llm_dev2',
        quotatype='auto',
        max_num_workers=32,
        task=dict(type=SubjectiveEvalTask),
    ),
)

work_dir = 'outputs/compass_arena/'

summarizer = dict(type=CompassArenaSummarizer, summary_type='half_add')