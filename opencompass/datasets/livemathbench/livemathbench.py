import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from functools import partial
from itertools import product
from typing import Any, Callable, Dict, List, Union

import jsonlines
import mmengine
from datasets import Dataset, load_dataset

from opencompass.datasets.math import math_postprocess_v2
from opencompass.models import OpenAISDK
from opencompass.openicl.icl_evaluator import GPassKEvaluator
from opencompass.openicl.icl_inferencer.icl_base_inferencer import \
    dump_results_dict
from opencompass.registry import ICL_EVALUATORS, LOAD_DATASET, MODELS
from opencompass.utils import get_data_path

from ..base import BaseDataset
from .prompts import (EXTRACT_PROMPT_CN, EXTRACT_PROMPT_EN, JUDGE_PROMPT_CN,
                      JUDGE_PROMPT_EN, PROMPT_CN, PROMPT_EN)
from .utils import extract_judge_label


@LOAD_DATASET.register_module()
class LiveMathBenchDataset(BaseDataset):

    @staticmethod
    def load(path: str,
             k: Union[int, List[int]],
             replication: int,
             dataset_splits: List[str] = [
                 'CNMO',
                 'CCEE',
                 'AMC',
                 'WLPMC',
             ],
             dataset_languages: List[str] = ['cn', 'en'],
             cot: bool = True,
             version: str = '202412') -> List[Dict[str, Any]]:
        dataset = []
        dataset_info = {}

        if path != '':
            path = get_data_path(path)
            head, tail = os.path.split(path)
            path = os.path.join(head, f'{tail}-{version}')
        for split, language in product(dataset_splits, dataset_languages):
            dataset_info[f'{split}_{language}'] = {
                'single-choice': 0,
                'multiple-choice': 0,
                'fill-in-the-blank': 0,
                'problem-solving': 0
            }
            question_type_mapping = {
                '单选': 'single-choice',
                '多选': 'multiple-choice',
                '填空': 'fill-in-the-blank',
                '问答': 'problem-solving'
            }

            if path != '':
                file_path = os.path.join(path, f'{split}_{language}.jsonl')
                if not os.path.exists(file_path):
                    continue
                examples = []
                with jsonlines.open(file_path, 'r') as file:
                    for example in file:
                        examples.append(example)
            else:
                hf_dataset = load_dataset(
                    'jnanliu/LiveMathBench',
                    f'v{version}_{split}_{language}')['test']
                examples = []
                for example in hf_dataset:
                    examples.append(example)

            for example_idx, example in enumerate(examples):
                dataset_info[f'{split}_{language}'][
                    example['question_type'] if language == 'en' else
                    question_type_mapping[example['question_type']]] += 1

                prompt = PROMPT_EN if language == 'en' else PROMPT_CN
                if not cot:
                    if language == 'cn':
                        prompt = prompt.replace('，请逐步推理', '')
                    else:
                        prompt = prompt.replace(
                            ', please reasoning step by step', '')
                example.update({
                    'subdivision':
                    f'{split}_{language}',
                    'idx':
                    str(example_idx),
                    'prompt':
                    prompt.format(question_type=example['question_type'],
                                  question=example['question'] +
                                  ('' if 'options' not in example else
                                   ' '.join(example['options']))),
                })
                max_k = k if isinstance(k, int) else max(k)
                for idx in range(max_k * replication):
                    duplicated_example = deepcopy(example)
                    duplicated_example.update({'replication_idx': idx})
                    dataset.append(duplicated_example)

        return Dataset.from_list(dataset)


@ICL_EVALUATORS.register_module()
class LiveMathBenchEvaluator(GPassKEvaluator):
    api_meta_template = dict(round=[
        dict(role='HUMAN', api_role='HUMAN'),
        dict(role='BOT', api_role='BOT', generate=True),
    ])

    def __init__(self,
                 model_name,
                 url,
                 use_extract_model=False,
                 extract_url=[],
                 extract_model_name='',
                 k: Union[int, List[int]] = 16,
                 replication: int = 3,
                 thresholds: List[float] = [0.0, 0.25, 0.5, 0.75, 1.0]):
        super().__init__(k, replication, thresholds)

        if isinstance(url, str):
            url = [url]

        self.judge_models = [
            MODELS.build(
                dict(
                    type=OpenAISDK,
                    path=model_name,
                    openai_api_base=_url,
                    key='EMPTY',
                    query_per_second=12,
                    meta_template=self.api_meta_template,
                    temperature=0.0,
                    max_seq_len=16384,
                )) for _url in url
        ]
        self.use_extract_model = use_extract_model
        self.extract_url = extract_url
        self.extract_model_name = extract_model_name

        self.extract_output_handler = LiveMathBenchOutputHandler()
        self.judge_output_handler = LiveMathBenchOutputHandler()

    def batch_infer(self, models: List[OpenAISDK], inputs: List[str],
                    completed_indexes: set,
                    output_handler: 'LiveMathBenchOutputHandler',
                    postprocess: Callable) -> List[str]:
        batch_size = 16
        batch_num = (len(inputs) + batch_size - 1) // batch_size
        all_indexes = [i for i in range(len(inputs))]
        indexes = [i for i in all_indexes if i not in completed_indexes]
        inputs = [inputs[i] for i in indexes]
        result_responses = []
        result_indexes = []

        def thread_worker(inputs, max_out_len, temperature, indexes, model):
            return model.generate(inputs, max_out_len, temperature), indexes

        if len(indexes) > 0:
            with ThreadPoolExecutor(max_workers=len(models)) as pool:
                tasks = [
                    pool.submit(
                        partial(thread_worker, model=models[i % len(models)]),
                        inputs[i * batch_size:(i + 1) * batch_size], 8192, 0.0,
                        indexes[i * batch_size:(i + 1) * batch_size])
                    for i in range(batch_num)
                ]
                for completed_task in as_completed(tasks):
                    responses, indexes = completed_task.result()
                    for input, response, index in zip(inputs, responses,
                                                      indexes):
                        output_handler.save(
                            index,
                            prompt=input,
                            response=response,
                            postprocess_response=postprocess(response))
                        result_responses.append(postprocess(response))
                        result_indexes.append(index)
                    output_handler.write_to_json()

        return [
            output_handler.output_dict[str(i)]['postprocess_response']
            for i in all_indexes
        ]

    def extract(self, questions: List[str], predictions: List[str],
                question_types: List[str], languages: List[str]) -> List[str]:

        # extract answer by model
        if self.use_extract_model:
            assert len(self.extract_url) > 0 and self.extract_model_name != ''
            extract_models = [
                MODELS.build(
                    dict(
                        type=OpenAISDK,
                        path=self.extract_model_name,
                        openai_api_base=url,
                        key='EMPTY',
                        query_per_second=1,
                        retry=1000,
                        meta_template=self.api_meta_template,
                        temperature=0.0,
                        max_seq_len=1024,
                    )) for url in self.extract_url
            ]

            completed_indexes = []
            mmengine.mkdir_or_exist(self.output_dir)
            tmp_json_file_path = os.path.join(self.output_dir,
                                              'tmp_extract.json')
            self.extract_output_handler.save_file_path = tmp_json_file_path
            if os.path.exists(tmp_json_file_path):
                tmp_dict = mmengine.load(tmp_json_file_path)
                self.extract_output_handler.output_dict = tmp_dict
                for index in tmp_dict:
                    completed_indexes.add(int(index))

            input_prompts = []
            for question, prediction, question_type, language in enumerate(
                    zip(questions, predictions, question_types, languages)):
                prompt = (EXTRACT_PROMPT_EN
                          if language == 'en' else EXTRACT_PROMPT_CN)
                input_prompts.append(
                    prompt.format(question=question,
                                  response=prediction,
                                  question_type=question_type))

            results = self.batch_infer(extract_models,
                                       input_prompts,
                                       completed_indexes,
                                       self.extract_output_handler,
                                       postprocess=lambda x: x)

            return results

        # extract answer in \\boxed{}
        results = [
            math_postprocess_v2(prediction) for prediction in predictions
        ]
        return results

    def judge(self, predictions, references, test_set):
        if len(predictions) != len(references):
            raise ValueError('preds and refrs have different length')

        completed_indexes = set()
        mmengine.mkdir_or_exist(self.output_dir)
        tmp_json_file_path = os.path.join(self.output_dir, 'tmp_judge.json')
        self.judge_output_handler.save_file_path = tmp_json_file_path
        if os.path.exists(tmp_json_file_path):
            tmp_dict = mmengine.load(tmp_json_file_path)
            self.judge_output_handler.output_dict = tmp_dict
            for index in tmp_dict:
                completed_indexes.add(int(index))

        questions = test_set['question']
        question_types = test_set['question_type']
        languages = [key.split('_')[1] for key in test_set['subdivision']]

        predictions = self.extract(questions, predictions, question_types,
                                   languages)

        inputs = []
        for prediction, reference, question, language in zip(
                predictions, references, questions, languages):
            prompt = JUDGE_PROMPT_EN if language == 'en' else JUDGE_PROMPT_CN
            inputs.append(
                prompt.format(answer=prediction,
                              gold_answer=reference,
                              question=question))

        labels = self.batch_infer(
            self.judge_models, inputs, completed_indexes,
            self.judge_output_handler, lambda x:
            (1 if extract_judge_label(x) == 'yes' else 0))
        return labels

    def preprocess(self, predictions, references, origin_prompt, test_set):
        return self.judge(predictions, references, test_set)


class LiveMathBenchOutputHandler:
    output_dict = {}
    save_file_path = ''

    def write_to_json(self):
        """Dump the result to a json file."""
        dump_results_dict(self.output_dict, self.save_file_path)

    def save(self, idx, **kwargs):
        self.output_dict[str(idx)] = kwargs
