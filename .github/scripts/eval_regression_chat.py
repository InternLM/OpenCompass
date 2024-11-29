from mmengine.config import read_base

with read_base():
    # choose a list of datasets
    from opencompass.configs.datasets.gsm8k.gsm8k_0shot_v2_gen_6e39a4 import \
        gsm8k_datasets  # noqa: F401, E501
    from opencompass.configs.datasets.race.race_gen import \
        race_datasets  # noqa: F401, E501
    # read hf models - chat models
    from opencompass.configs.models.baichuan.hf_baichuan2_7b_chat import \
        models as hf_baichuan2_7b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.chatglm.hf_glm4_9b_chat import \
        models as hf_glm4_9b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.chatglm.lmdeploy_glm4_9b_chat import \
        models as lmdeploy_glm4_9b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.chatglm.vllm_glm4_9b_chat import \
        models as vllm_glm4_9b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.deepseek.hf_deepseek_7b_chat import \
        models as hf_deepseek_7b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.deepseek.hf_deepseek_moe_16b_chat import \
        models as hf_deepseek_moe_16b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.deepseek.hf_deepseek_v2_lite_chat import \
        models as hf_deepseek_v2_lite_chat_model  # noqa: F401, E501
    from opencompass.configs.models.deepseek.vllm_deepseek_7b_chat import \
        models as vllm_deepseek_7b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.gemma.hf_gemma2_2b_it import \
        models as hf_gemma2_2b_it_model  # noqa: F401, E501
    from opencompass.configs.models.gemma.hf_gemma2_9b_it import \
        models as hf_gemma2_9b_it_model  # noqa: F401, E501
    from opencompass.configs.models.gemma.hf_gemma_2b_it import \
        models as hf_gemma_2b_it_model  # noqa: F401, E501
    from opencompass.configs.models.gemma.hf_gemma_7b_it import \
        models as hf_gemma_7b_it_model  # noqa: F401, E501
    from opencompass.configs.models.gemma.lmdeploy_gemma_9b_it import \
        models as lmdeploy_gemma_9b_it_model  # noqa: F401, E501
    from opencompass.configs.models.gemma.vllm_gemma_7b_it import \
        models as vllm_gemma_7b_it_model  # noqa: F401, E501
    from opencompass.configs.models.hf_internlm.hf_internlm2_5_7b_chat import \
        models as hf_internlm2_5_7b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.hf_internlm.hf_internlm2_5_20b_chat import \
        models as hf_internlm2_5_20b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.hf_internlm.lmdeploy_internlm2_5_7b_chat import \
        models as lmdeploy_internlm2_5_7b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.hf_internlm.lmdeploy_internlm2_5_20b_chat import \
        models as lmdeploy_internlm2_5_20b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.hf_internlm.lmdeploy_internlm2_chat_1_8b import \
        models as lmdeploy_internlm2_chat_1_8b_model  # noqa: F401, E501
    from opencompass.configs.models.hf_internlm.lmdeploy_internlm2_chat_1_8b_sft import \
        models as lmdeploy_internlm2_chat_1_8b_sft_model  # noqa: F401, E501
    from opencompass.configs.models.hf_internlm.lmdeploy_internlm2_chat_7b import \
        models as lmdeploy_internlm2_chat_7b_model  # noqa: F401, E501
    from opencompass.configs.models.hf_internlm.lmdeploy_internlm2_chat_7b_sft import \
        models as lmdeploy_internlm2_chat_7b_sft_model  # noqa: F401, E501
    from opencompass.configs.models.hf_internlm.vllm_internlm2_chat_7b import \
        models as vllm_internlm2_chat_7b_model  # noqa: F401, E501
    from opencompass.configs.models.hf_llama.hf_llama3_1_8b_instruct import \
        models as hf_llama3_1_8b_instruct_model  # noqa: F401, E501
    from opencompass.configs.models.hf_llama.hf_llama3_2_3b_instruct import \
        models as hf_llama3_2_3b_instruct_model  # noqa: F401, E501
    from opencompass.configs.models.hf_llama.hf_llama3_8b_instruct import \
        models as hf_llama3_8b_instruct_model  # noqa: F401, E501
    from opencompass.configs.models.hf_llama.lmdeploy_llama2_7b_chat import \
        models as lmdeploy_llama2_7b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.hf_llama.lmdeploy_llama3_1_8b_instruct import \
        models as lmdeploy_llama3_1_8b_instruct_model  # noqa: F401, E501
    from opencompass.configs.models.hf_llama.lmdeploy_llama3_2_3b_instruct import \
        models as lmdeploy_llama3_2_3b_instruct_model  # noqa: F401, E501
    from opencompass.configs.models.hf_llama.lmdeploy_llama3_8b_instruct import \
        models as lmdeploy_llama3_8b_instruct_model  # noqa: F401, E501
    from opencompass.configs.models.mistral.hf_mistral_7b_instruct_v0_2 import \
        models as hf_mistral_7b_instruct_v0_2_model  # noqa: F401, E501
    from opencompass.configs.models.mistral.hf_mistral_7b_instruct_v0_3 import \
        models as hf_mistral_7b_instruct_v0_3_model  # noqa: F401, E501
    from opencompass.configs.models.mistral.hf_mistral_nemo_instruct_2407 import \
        models as hf_mistral_nemo_instruct_2407_model  # noqa: F401, E501
    from opencompass.configs.models.mistral.hf_mistral_small_instruct_2409 import \
        models as hf_mistral_small_instruct_2409_model  # noqa: F401, E501
    from opencompass.configs.models.mistral.lmdeploy_mistral_nemo_instruct_2407 import \
        models as lmdeploy_mistral_nemo_instruct_2407_model  # noqa: F401, E501
    from opencompass.configs.models.mistral.lmdeploy_mistral_small_instruct_2409 import \
        models as \
        lmdeploy_mistral_small_instruct_2409_model  # noqa: F401, E501
    from opencompass.configs.models.mistral.vllm_mistral_7b_instruct_v0_1 import \
        models as vllm_mistral_7b_instruct_v0_1_model  # noqa: F401, E501
    from opencompass.configs.models.mistral.vllm_mistral_7b_instruct_v0_2 import \
        models as vllm_mistral_7b_instruct_v0_2_model  # noqa: F401, E501
    from opencompass.configs.models.openbmb.hf_minicpm3_4b import \
        models as hf_minicpm3_4b_model  # noqa: F401, E501
    from opencompass.configs.models.openbmb.hf_minicpm_2b_dpo_fp32 import \
        models as hf_minicpm_2b_dpo_fp32_model  # noqa: F401, E501
    from opencompass.configs.models.openbmb.hf_minicpm_2b_sft_bf16 import \
        models as hf_minicpm_2b_sft_bf16_model  # noqa: F401, E501
    from opencompass.configs.models.openbmb.hf_minicpm_2b_sft_fp32 import \
        models as hf_minicpm_2b_sft_fp32_model  # noqa: F401, E501
    from opencompass.configs.models.phi.hf_phi_3_mini_4k_instruct import \
        models as hf_phi_3_mini_4k_instruct_model  # noqa: F401, E501
    from opencompass.configs.models.phi.hf_phi_3_small_8k_instruct import \
        models as hf_phi_3_mini_8k_instruct_model  # noqa: F401, E501
    from opencompass.configs.models.qwen2_5.hf_qwen2_5_14b_instruct import \
        models as hf_qwen2_5_14b_instruct_model  # noqa: F401, E501
    from opencompass.configs.models.qwen2_5.lmdeploy_qwen2_5_14b_instruct import \
        models as lmdeploy_qwen2_5_14b_instruct_model  # noqa: F401, E501
    from opencompass.configs.models.qwen.hf_qwen1_5_0_5b_chat import \
        models as hf_qwen1_5_0_5b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.qwen.hf_qwen2_1_5b_instruct import \
        models as hf_qwen2_1_5b_instruct_model  # noqa: F401, E501
    from opencompass.configs.models.qwen.hf_qwen2_7b_instruct import \
        models as hf_qwen2_7b_instruct_model  # noqa: F401, E501
    from opencompass.configs.models.qwen.lmdeploy_qwen2_1_5b_instruct import \
        models as lmdeploy_qwen2_1_5b_instruct_model  # noqa: F401, E501
    from opencompass.configs.models.qwen.lmdeploy_qwen2_7b_instruct import \
        models as lmdeploy_qwen2_7b_instruct_model  # noqa: F401, E501
    from opencompass.configs.models.qwen.vllm_qwen1_5_0_5b_chat import \
        models as vllm_qwen1_5_0_5b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.yi.hf_yi_1_5_6b_chat import \
        models as hf_yi_1_5_6b_chat_model  # noqa: F401, E501
    from opencompass.configs.models.yi.hf_yi_1_5_9b_chat import \
        models as hf_yi_1_5_9b_chat_model  # noqa: F401, E501

race_datasets = [race_datasets[1]]
datasets = sum([v for k, v in locals().items() if k.endswith('_datasets')], [])

api_meta_template = dict(
    round=[
        dict(role='HUMAN', api_role='HUMAN'),
        dict(role='BOT', api_role='BOT', generate=True),
    ],
    reserved_roles=[dict(role='SYSTEM', api_role='SYSTEM')],
)

for d in datasets:
    d['reader_cfg']['test_range'] = '[0:32]'

models = sum([v for k, v in locals().items() if k.endswith('_model')], [])

for m in models:
    if 'turbomind' in m['abbr'] or 'lmdeploy' in m['abbr']:
        m['engine_config']['max_batch_size'] = 1
        m['batch_size'] = 1

models = sorted(models, key=lambda x: x['run_cfg']['num_gpus'])

summarizer = dict(
    dataset_abbrs=[
        'gsm8k',
        'race-middle',
        'race-high',
    ],
    summary_groups=sum(
        [v for k, v in locals().items() if k.endswith('_summary_groups')], []),
)
