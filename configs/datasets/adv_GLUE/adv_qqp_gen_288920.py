from opencompass.openicl.icl_prompt_template import PromptTemplate
from opencompass.openicl.icl_retriever import ZeroRetriever
from opencompass.openicl.icl_inferencer import GenInferencer
from opencompass.openicl.icl_evaluator import AccEvaluator
from opencompass.datasets import adv_qqpDataset
from opencompass.utils.text_postprocessors import first_capital_postprocess

adv_qqp_reader_cfg = dict(
    input_columns=['question1', 'question2'],
    output_column='label_option',
    train_split='validation',
    test_split='validation')

adv_qqp_infer_cfg = dict(
    prompt_template=dict(
        type=PromptTemplate,
        template=dict(round=[
            dict(
                role='HUMAN',
                prompt=
                """Please identify whether Question 1 has the same meaning as Question 2. The answer should be exactly 'A. no' or 'B. yes'.
Question 1: {question1}
Question 2: {question2}
Answer:"""),
        ]),
    ),
    retriever=dict(type=ZeroRetriever),
    inferencer=dict(type=GenInferencer),
)

adv_qqp_eval_cfg = dict(
    evaluator=dict(type=AccEvaluator),
    pred_role="BOT",
    pred_postprocessor=dict(type=first_capital_postprocess),
)

adv_qqp_datasets = [
    dict(
        abbr='adv_qqp',
        type=adv_qqpDataset,
        path='adv_glue',
        name='adv_qqp',
        reader_cfg=adv_qqp_reader_cfg,
        infer_cfg=adv_qqp_infer_cfg,
        eval_cfg=adv_qqp_eval_cfg,
    )
]
