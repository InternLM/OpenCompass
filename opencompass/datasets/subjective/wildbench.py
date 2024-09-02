import json

from datasets import Dataset, DatasetDict

from opencompass.registry import LOAD_DATASET
from opencompass.utils import get_data_path

from ..base import BaseDataset

score_prompt = """# Instruction

You are an expert evaluator. Your task is to evaluate the quality of \
the responses generated by AI models.
We will provide you with the user query and an AI-generated responses.
You should first read the user query and the conversation history \
carefully for analyzing the task, and then evaluate the quality of \
the responses based on and rules provided below.

# Conversation between User and AI

## History
<|begin_of_history|>

{history}

<|end_of_history|>

## Current User Query
<|begin_of_query|>

{user_query}

<|end_of_query|>

## AI Response
<|begin_of_response|>

{prediction}

<|end_of_response|>


# Evaluation

## Checklist

<|begin_of_checklist|>

{checklist}

<|end_of_checklist|>

Please use this checklist to guide your evaluation, but do \
not limit your assessment to the checklist.

## Rules

You should compare the above response based on your analysis\
 of the user queries and the conversation history.
You should first write down your analysis and the checklist \
that you used for the evaluation, and then provide your \
assessment according to the checklist.
The scores are in the range of 1~10, where 1 means the \
response is very poor and 10 means the response is perfect.
Here are more detailed criteria for the scores:

- Score 1~2: The response is very poor and does not make sense at all.
- Score 3~4: The response is poor and does help user solve the problem\
 in a meaningful way.
- Score 5~6: The response is fair but has some issues (e.g., factual \
errors, hallucinations, missing key information).
- Score 7~8: The response is good enough but could be improved in some ways.
- Score 9~10: The response is perfect and provides helpful information that\
 can help user solve the problem.

## Output Format
First, please output your analysis for the model response, and then summarize\
 your assessment to two aspects: "strengths" and "weaknesses"; Finally, please\
 write down your rating for the assessment.

Please provide your evaluation results in the following json format by filling\
 in the placeholders in []:
```
{
    "strengths": "[analysis for the strengths of the response]",
    "weaknesses": "[analysis for the weaknesses of the response]",
    "score": "[1~10]"
}
```"""

pair_prompt = """# Instruction

You are an expert evaluator. Your task is to evaluate the quality of the \
responses generated by two AI models.
We will provide you with the user query and a pair of AI-generated \
responses (Response A and Response B).
You should first read the user query and the conversation history \
carefully for analyzing the task, and then evaluate the quality of the \
responses based on and rules provided below.

# Conversation between User and AI

## History
<|begin_of_history|>

{history}

<|end_of_history|>

## Current User Query
<|begin_of_query|>

{user_query}

<|end_of_query|>

## Response A
<|begin_of_response_A|>

{prediction}

<|end_of_response_A|>

## Response B
<|begin_of_response_B|>

{prediction2}

<|end_of_response_B|>

# Evaluation

## Checklist

<|begin_of_checklist|>

{checklist}

<|end_of_checklist|>

Please use this checklist to guide your evaluation, but do not limit your \
assessment to the checklist.

## Rules

You should compare the above two responses based on your analysis of the \
user queries and the conversation history.
You should first write down your analysis and the checklist that you used \
for the evaluation, and then provide your assessment according to the \
checklist.
There are five choices to give your final assessment: ["A++", "A+", \
"A=B", "B+", "B++"], which correspond to the following meanings:

- `A++`: Response A is much better than Response B.
- `A+`: Response A is only slightly better than Response B.
- `A=B`: Response A and B are of the same quality. Please use this \
choice sparingly.
- `B+`: Response B is only slightly better than Response A.
- `B++`: Response B is much better than Response A.


## Output Format
First, please output your analysis for each model response, and \
then summarize your assessment to three aspects: "reason A=B", \
"reason A>B", and "reason B>A", and finally make your choice for \
the final assessment.

Please provide your evaluation results in the following json \
format by filling in the placeholders in []:
```
{
    "analysis of A": "[analysis of Response A]",
    "analysis of B": "[analysis of Response B]",
    "reason of A=B": "[where Response A and B perform equally well]",
    "reason of A>B": "[where Response A is better than Response B]",
    "reason of B>A": "[where Response B is better than Response A]",
    "choice": "[A++ or A+ or A=B or B+ or B++]",
}
```
"""


def parse_conversation(conversation):
    # parse conversation into chat dialogue
    role_dict = {'user': 'HUMAN', 'assistant': 'assistant'}
    chat_round = []
    history = ''
    if len(conversation) > 0:
        for x in conversation[:-1]:
            if x['role'] == 'user':
                history += 'USER: ' + x['content'] + '\n\n'
            elif x['role'] == 'assistant':
                history += 'ASSISTANT: ' + x['content'] + '\n\n'

            chat_round.append({
                'role': role_dict[x['role']],
                'content': x['content']
            })

    last_query = conversation[-1]['content']
    chat_round.append({
        'role': role_dict[conversation[-1]['role']],
        'content': conversation[-1]['content']
    })
    chat_round.append({'role': 'assistant', 'content': ''})

    return chat_round, last_query, history


@LOAD_DATASET.register_module()
class WildBenchDataset(BaseDataset):

    def load(self, path: str, K=-1, eval_mode='pair', *args, **kwargs):
        path = get_data_path(path, local_mode=True)
        dataset = DatasetDict()
        raw_data = []
        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                item = json.loads(line)
                chat_round, last_query, history = parse_conversation(
                    item['turn'])

                checklist_mardkdown = ''
                for checklist_item in item['checklist']:
                    checklist_mardkdown += f'- {checklist_item}\n'

                if eval_mode == 'single':
                    prompt = score_prompt
                elif eval_mode == 'pair':
                    prompt = pair_prompt
                else:
                    assert NotImplementedError(
                        f'Eval mode {eval_mode} not in single or pair.')

                prompt = prompt.replace('{history}', history)
                prompt = prompt.replace('{user_query}', last_query)
                prompt = prompt.replace('{checklist}', checklist_mardkdown)

                raw_data.append({
                    'dialogue': chat_round,
                    'history': history,
                    'prompt': prompt,
                    'judge': {
                        'other': None,
                        'primary_tag': item['primary_tag'],
                        'secondary_tag': item['secondary_tag'],
                        'question_id': item['session_id'],
                    }
                })
        dataset = Dataset.from_list(raw_data)
        return dataset
