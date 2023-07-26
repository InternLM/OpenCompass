from opencompass.openicl.icl_prompt_template import PromptTemplate
from opencompass.openicl.icl_retriever import ZeroRetriever
from opencompass.openicl.icl_inferencer import GenInferencer
from opencompass.openicl.icl_evaluator import AccEvaluator
from opencompass.datasets import adv_mnliDataset
from opencompass.utils.text_postprocessors import first_capital_postprocess

adv_mnli_reader_cfg = dict(
    input_columns=['premise', 'hypothesis'],
    output_column='label_option',
    train_split='validation',
    test_split='validation')

adv_mnli_infer_cfg = dict(
    prompt_template=dict(
        type=PromptTemplate,
        template=dict(round=[
            dict(
                role='HUMAN',
                prompt=
                """Please identify whether the premise entails the hypothesis. The answer should be exactly 'A. yes', 'B. maybe' or 'C. no'.
premise: {premise}
hypothesis: {hypothesis}
Answer:"""),
        ]),
    ),
    retriever=dict(type=ZeroRetriever),
    inferencer=dict(type=GenInferencer),
)

adv_mnli_eval_cfg = dict(
    evaluator=dict(type=AccEvaluator),
    pred_role="BOT",
    pred_postprocessor=dict(type=first_capital_postprocess),
)

adv_mnli_datasets = [
    dict(
        abbr='adv_mnli',
        type=adv_mnliDataset,
        path='adv_glue',
        name='adv_mnli',
        reader_cfg=adv_mnli_reader_cfg,
        infer_cfg=adv_mnli_infer_cfg,
        eval_cfg=adv_mnli_eval_cfg,
    )
]
