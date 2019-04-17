import os
import sh
from io import StringIO
from .util import build_temp_zipfiles, build_directories, unzip_files


def handle(request):
    """
    handle a request to the function
    Args:
        request (str): request body
    """
    zip_file = request.files.getlist('files')[0]
    cpplint_reports = []
    with tempfile.TemporaryDirectory() as tmpdir:
        unzip_files(zip_file, tmpdir)
        with open(f'{tmpdir}/run_vars.yml') as o:
            run_vars = yaml.safe_load(o)
        os.chdir(tmpdir)
        project_directories = [name for name in os.listdir(".") if os.path.isdir(name)]
        for project_directory in project_directories:
            report = run_cpplint(project_directory)
            cpplint_reports.append(report)
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
