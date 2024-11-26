import json
import os
import os.path as osp
import random
import re
import subprocess
import time
import warnings
from functools import partial
from json import JSONDecodeError
from typing import Any, Dict, List, Optional, Tuple

import mmengine
import yaml
from mmengine.config import ConfigDict
from mmengine.utils import track_parallel_progress

from opencompass.registry import RUNNERS, TASKS
from opencompass.utils import StrEnum, get_logger

from .base import BaseRunner


class VolcStatus(StrEnum):
    success = 'Success'
    failed = 'Failed'
    cancelled = 'Cancelled'
    exception = 'Exception'
    killing = 'Killing'
    success_holding = 'SuccessHolding'
    failed_holding = 'FailedHolding'
    queue = 'Queue'


@RUNNERS.register_module()
class VOLCRunner(BaseRunner):
    """Distributed runner based on Volcano Cloud Cluster (VCC). It will launch
    multiple tasks in parallel with the 'vcc' command. Please install and
    configure VCC first before using this runner.

    Args:
        task (ConfigDict): Task type config.
        volcano_cfg (ConfigDict): Volcano Cloud config.
        queue_name (str): Name of resource queue.
        preemptible (bool): Whether to launch task in preemptible way.
            Default: False
        priority (bool): Priority of tasks, ranging from 1 to 9.
            9 means the highest priority. Default: None
        max_num_workers (int): Max number of workers. Default: 32.
        retry (int): Number of retries when job failed. Default: 2.
        debug (bool): Whether to run in debug mode. Default: False.
        lark_bot_url (str): Lark bot url. Default: None.
    """

    def __init__(self,
                 task: ConfigDict,
                 volcano_cfg: ConfigDict,
                 queue_name: str,
                 preemptible: bool = False,
                 priority: Optional[int] = None,
                 max_num_workers: int = 32,
                 retry: int = 2,
                 debug: bool = False,
                 lark_bot_url: str = None,
                 keep_tmp_file: bool = False):
        super().__init__(task=task, debug=debug, lark_bot_url=lark_bot_url)
        self.volcano_cfg = volcano_cfg
        self.max_num_workers = max_num_workers
        self.retry = retry
        self.queue_name = queue_name
        self.preemptible = preemptible
        self.priority = priority
        self.keep_tmp_file = keep_tmp_file

    def launch(self, tasks: List[Dict[str, Any]]) -> List[Tuple[str, int]]:
        """Launch multiple tasks.

        Args:
            tasks (list[dict]): A list of task configs, usually generated by
                Partitioner.

        Returns:
            list[tuple[str, int]]: A list of (task name, exit code).
        """

        if not self.debug:
            status = track_parallel_progress(self._launch,
                                             tasks,
                                             nproc=self.max_num_workers,
                                             keep_order=False)
        else:
            status = [self._launch(task, random_sleep=False) for task in tasks]
        return status

    def _launch(self, task_cfg: ConfigDict, random_sleep: bool = True):
        """Launch a single task.

        Args:
            task_cfg (ConfigDict): Task config.
            random_sleep (bool): Whether to sleep for a random time before
                running the command. This avoids cluster error when launching
                multiple tasks at the same time. Default: True.

        Returns:
            tuple[str, int]: Task name and exit code.
        """

        task_type = self.task_cfg.type
        if isinstance(self.task_cfg.type, str):
            task_type = TASKS.get(task_type)
        task = task_type(task_cfg)
        num_gpus = task.num_gpus
        task_name = task.name

        # Build up VCC command
        pwd = os.getcwd()
        # Dump task config to file
        mmengine.mkdir_or_exist('tmp/')
        # Using uuid to avoid filename conflict
        import uuid
        uuid_str = str(uuid.uuid4())
        param_file = f'{pwd}/tmp/{uuid_str}_params.py'

        volc_cfg_file = f'{pwd}/tmp/{uuid_str}_cfg.yaml'
        volc_cfg = self._choose_flavor(num_gpus)
        with open(volc_cfg_file, 'w') as fp:
            yaml.dump(volc_cfg, fp, sort_keys=False)
        try:
            task_cfg.dump(param_file)
            if self.volcano_cfg.get('bashrc_path') is not None:
                # using user's conda env
                bashrc_path = self.volcano_cfg['bashrc_path']
                assert osp.exists(bashrc_path)
                assert self.volcano_cfg.get('conda_env_name') is not None

                conda_env_name = self.volcano_cfg['conda_env_name']

                shell_cmd = (f"source {self.volcano_cfg['bashrc_path']}; "
                             f'source activate {conda_env_name}; ')
                shell_cmd += f'export PYTHONPATH={pwd}:$PYTHONPATH; '
            else:
                assert self.volcano_cfg.get('python_env_path') is not None
                shell_cmd = (
                    f"export PATH={self.volcano_cfg['python_env_path']}/bin:$PATH; "  # noqa: E501
                    f'export PYTHONPATH={pwd}:$PYTHONPATH; ')

            huggingface_cache = self.volcano_cfg.get('huggingface_cache')
            if huggingface_cache is not None:
                # HUGGINGFACE_HUB_CACHE is a Legacy env variable, here we set
                # `HF_HUB_CACHE` and `HUGGINGFACE_HUB_CACHE` for bc
                shell_cmd += f'export HF_HUB_CACHE={huggingface_cache}; '
                shell_cmd += f'export HUGGINGFACE_HUB_CACHE={huggingface_cache}; '  # noqa: E501

            torch_cache = self.volcano_cfg.get('torch_cache')
            if torch_cache is not None:
                shell_cmd += f'export TORCH_HOME={torch_cache}; '

            hf_offline = self.volcano_cfg.get('hf_offline', True)

            if hf_offline:
                shell_cmd += 'export HF_DATASETS_OFFLINE=1; export TRANSFORMERS_OFFLINE=1; export HF_EVALUATE_OFFLINE=1; export HF_HUB_OFFLINE=1; '  # noqa: E501

            hf_endpoint = self.volcano_cfg.get('hf_endpoint')
            if hf_endpoint is not None:
                shell_cmd += f'export HF_ENDPOINT={hf_endpoint}; '

            extra_envs = self.volcano_cfg.get('extra_envs')
            if extra_envs is not None:
                for extra_env in extra_envs:
                    shell_cmd += f'export {extra_env}; '

            shell_cmd += f'cd {pwd}; '
            shell_cmd += '{task_cmd}'

            task_name = task_name[:128].replace('[', '-').replace(
                ']', '').replace('/', '-').replace(',',
                                                   '--').replace('.', '_')
            tmpl = ('volc ml_task submit'
                    f" --conf '{volc_cfg_file}'"
                    f" --entrypoint '{shell_cmd}'"
                    f' --task_name {task_name}'
                    f' --resource_queue_name {self.queue_name}')
            if self.preemptible:
                tmpl += ' --preemptible'
            if self.priority is not None:
                tmpl += f' --priority {self.priority}'
            get_cmd = partial(task.get_command,
                              cfg_path=param_file,
                              template=tmpl)
            cmd = get_cmd()

            logger = get_logger()
            logger.debug(f'Running command: {cmd}')

            out_path = task.get_log_path(file_extension='txt')
            mmengine.mkdir_or_exist(osp.split(out_path)[0])

            retry = self.retry
            while True:
                task_status, returncode = self._run_task(cmd,
                                                         out_path,
                                                         poll_interval=20)
                output_paths = task.get_output_paths()
                if not (self._job_failed(task_status, output_paths)) \
                        or retry <= 0:
                    break
                if random_sleep:
                    time.sleep(random.randint(0, 10))
                retry -= 1

        finally:
            # Clean up
            if not self.keep_tmp_file:
                os.remove(param_file)
                os.remove(volc_cfg_file)
            else:
                pass

        return task_name, returncode

    def _run_task(self, cmd, log_path, poll_interval):
        result = subprocess.run(cmd,
                                shell=True,
                                text=True,
                                capture_output=True)
        f = open(log_path, 'w')
        pattern = r'(?<=task_id=).*(?=\n\n)'
        match = re.search(pattern, result.stdout)
        if match:
            task_id = match.group()
            ask_cmd = f'volc ml_task get --id {task_id} --output json ' + \
                      '--format Status'
            log_cmd = f'volc ml_task logs --task {task_id} --instance worker_0'
            while True:
                ret = subprocess.run(ask_cmd,
                                     shell=True,
                                     text=True,
                                     capture_output=True)
                try:
                    task_status = json.loads(
                        ret.stdout.split()[-1])[0]['Status']
                except JSONDecodeError:
                    print('The task is not yet in the queue for '
                          f'{ret.stdout}, waiting...')
                    time.sleep(poll_interval)
                    continue
                finally:
                    if task_status not in VolcStatus.__members__.values():
                        warnings.warn(
                            f'Unrecognized task status: {task_status}. '
                            'This might be due to a newer version of Volc. '
                            'Please report this issue to the OpenCompass.')

                if task_status != VolcStatus.queue:
                    # Record task status when jobs is in Queue
                    f.write(ret.stdout or ret.stderr)
                    f.flush()
                    time.sleep(poll_interval)
                    continue

                if self.debug:
                    print(task_status)

                # TODO: volc log cmd is broken now, this should be double
                # checked when log cli is fixed
                ret = subprocess.run(log_cmd,
                                     shell=True,
                                     text=True,
                                     capture_output=True)

                f.write(log_cmd)
                f.write(ret.stdout)
                f.flush()
                time.sleep(poll_interval)

                if task_status in [
                        VolcStatus.success,
                        VolcStatus.success_holding,
                ]:
                    break
                else:
                    time.sleep(poll_interval)
                    continue
        else:
            print(f'Failed to submit the task for：{result.stdout}')
            task_status = VolcStatus.exception
            f.write(f'{result.stdout}: {result.returncode}')

        f.close()
        return task_status, result.returncode

    def _job_failed(self, task_status: str, output_paths: List[str]) -> bool:
        return task_status not in [
            VolcStatus.success, VolcStatus.success_holding
        ] or not all(osp.exists(output_path) for output_path in output_paths)

    def _choose_flavor(self, num_gpus):
        config_path = self.volcano_cfg.volcano_config_path
        with open(config_path) as fp:
            volc_cfg = yaml.safe_load(fp)
        if num_gpus <= 0:
            flavor = 'ml.c3i.2xlarge'
        elif num_gpus == 1:
            flavor = 'ml.pni2l.3xlarge'
        elif num_gpus == 2:
            flavor = 'ml.pni2l.7xlarge'
        elif num_gpus <= 4:
            flavor = 'ml.pni2l.14xlarge'
        elif num_gpus <= 8:
            flavor = 'ml.pni2l.28xlarge'
        else:
            raise NotImplementedError

        role_specs = volc_cfg['TaskRoleSpecs']
        for i in range(len(role_specs)):
            if role_specs[i]['RoleName'] == 'worker':
                role_specs[i]['Flavor'] = flavor

        return volc_cfg
