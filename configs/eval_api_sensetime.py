from mmengine.config import read_base
from opencompass.models import SenseTime
from opencompass.partitioners import NaivePartitioner
from opencompass.runners import LocalRunner
from opencompass.runners.local_api import LocalAPIRunner
from opencompass.tasks import OpenICLInferTask

with read_base():
    # from .datasets.collections.chat_medium import datasets
    from .summarizers.medium import summarizer
    from .datasets.ceval.ceval_gen import ceval_datasets

datasets = [
    *ceval_datasets,
]

models = [
    dict(
        abbr='nova-ptc-xl-v1',
        type=SenseTime,
        path='nova-ptc-xl-v1',
        key='xxxxxxxxxxxxxx',
        url='xxxxxxxxxxx',
        query_per_second=1,
        max_out_len=2048,
        max_seq_len=2048,
        batch_size=8),
]

infer = dict(
    partitioner=dict(type=NaivePartitioner),
    runner=dict(
        type=LocalAPIRunner,
        max_num_workers=2,
        concurrent_users=2,
        task=dict(type=OpenICLInferTask)),
)
