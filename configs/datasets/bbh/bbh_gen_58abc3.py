from os.path import exists
from opencompass.openicl.icl_prompt_template import PromptTemplate
from opencompass.openicl.icl_retriever import ZeroRetriever
from opencompass.openicl.icl_inferencer import GenInferencer
from opencompass.openicl.icl_evaluator import AccEvaluator
from opencompass.datasets import BBHDataset, BBHEvaluator

bbh_reader_cfg = dict(input_columns=["input"], output_column="target")

_path_prefix = "./data/BBH"

bbh_multiple_choice_sets = [
    'temporal_sequences',
    'disambiguation_qa',
    'date_understanding',
    'tracking_shuffled_objects_three_objects',
    'penguins_in_a_table',
    'geometric_shapes',
    'snarks',
    'ruin_names',
    'tracking_shuffled_objects_seven_objects',
    'tracking_shuffled_objects_five_objects',
    'logical_deduction_three_objects',
    'hyperbaton',
    'logical_deduction_five_objects',
    'logical_deduction_seven_objects',
    'movie_recommendation',
    'salient_translation_error_detection',
    'reasoning_about_colored_objects',
]
bbh_free_form_sets = [
    'multistep_arithmetic_two',
    'navigate',
    'dyck_languages',
    'word_sorting',
    'sports_understanding',
    'boolean_expressions',
    'object_counting',
    'formal_fallacies',
    'causal_judgement',
    'web_of_lies',
]

bbh_datasets = []
for _name in bbh_multiple_choice_sets:
    _hint = None
    if exists(f"{_path_prefix}/lib_prompt/{_name}.txt"):
        _hint = open(f"{_path_prefix}/lib_prompt/{_name}.txt", 'r').read()
    bbh_infer_cfg = dict(
        prompt_template=dict(
            type=PromptTemplate,
            template=dict(round=[
                dict(
                    role="HUMAN",
                    prompt=
                    f"Follow the given examples and answer the question.\n{_hint}\n\nQ: {{input}}\nA: Let's think step by step."
                )
            ])),
        retriever=dict(type=ZeroRetriever),
        inferencer=dict(type=GenInferencer, max_out_len=512))
    bbh_eval_cfg = dict(
        evaluator=dict(type=AccEvaluator),
        pred_role="BOT",
        pred_postprocessor=dict(type='bbh-mcq'),
        dataset_postprocessor=dict(type='bbh-mcq'))

    bbh_datasets.append(
        dict(
            type=BBHDataset,
            path=f"{_path_prefix}/data",
            name=_name,
            abbr='bbh-' + _name,
            reader_cfg=bbh_reader_cfg,
            infer_cfg=bbh_infer_cfg.copy(),
            eval_cfg=bbh_eval_cfg.copy()))

for _name in bbh_free_form_sets:
    _hint = None
    if exists(f"{_path_prefix}/lib_prompt/{_name}.txt"):
        _hint = open(f"{_path_prefix}/lib_prompt/{_name}.txt", 'r').read()
    bbh_infer_cfg = dict(
        prompt_template=dict(
            type=PromptTemplate,
            template=dict(round=[
                dict(
                    role="HUMAN",
                    prompt=
                    f"Follow the given examples and answer the question.\n{_hint}\n\nQ: {{input}}\nA: Let's think step by step."
                )
            ])),
        retriever=dict(type=ZeroRetriever),
        inferencer=dict(type=GenInferencer, max_out_len=512))
    bbh_eval_cfg = dict(evaluator=dict(type=BBHEvaluator), pred_role="BOT")

    bbh_datasets.append(
        dict(
            type=BBHDataset,
            path=f"{_path_prefix}/data",
            name=_name,
            abbr='bbh-' + _name,
            reader_cfg=bbh_reader_cfg,
            infer_cfg=bbh_infer_cfg.copy(),
            eval_cfg=bbh_eval_cfg.copy()))

del _name, _hint, _path_prefix
