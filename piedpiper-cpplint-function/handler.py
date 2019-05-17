import os
import tempfile
import sh
import yaml
from io import StringIO
from .util import unzip_files, upload_artifact, download_artifact, read_secrets, update_task_id_status
from .config import Config

gman_url = Config['gman']['url']
storage_url = Config['storage']['url']


def handle(request):
    """
    handle a request to the function
    Args:
        request (str): request body
    """
    run_id = request.get_json().get('run_id')
    task_id = request.get_json()['task_id']

    access_key = read_secrets().get('access_key')
    secret_key = read_secrets().get('secret_key')

    update_task_id_status(gman_url=gman_url, status='received', task_id=task_id,
                          message='Received execution task from cpplint gateway')

    with tempfile.TemporaryDirectory() as temp_directory:
        download_artifact(run_id, 'artifacts/cpplint.zip', f'{temp_directory}/cpplint.zip', storage_url,
                          access_key, secret_key)
        cpplint_reports = []
        unzip_files(f'{temp_directory}/cpplint.zip', temp_directory)
        os.chdir(temp_directory)
        project_directories = [
            name
            for name in os.listdir(".")
            if os.path.isdir(name)
        ]
        for project_directory in project_directories:
            report = run_cpplint(project_directory)
            cpplint_reports.append(report)

        log_file = f'{temp_directory}/cpplint.log'
        with open(log_file, 'w') as f:
            f.write(yaml.safe_dump(cpplint_reports))
        upload_artifact(run_id, 'artifacts/cpplint.log', log_file, storage_url, access_key, secret_key)
        update_task_id_status(gman_url=gman_url, task_id=task_id,
                              status='completed', message=' execution complete')
    return '\n'.join(cpplint_reports)


def run_cpplint(directory):
    buf = StringIO()
    try:
        sh.cpplint(
            '--recursive',
            f'--repository={directory}',
            directory,
            _err=buf
        )
    except sh.ErrorReturnCode_1:
        pass
    return buf.getvalue()
