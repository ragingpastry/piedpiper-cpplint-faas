import os
import sh
from io import StringIO
from .util import build_temp_zipfiles, build_directories, unzip_files


def handle(request):
    """handle a request to the function
    Args:
        req (str): request body
    """

    zip_files = build_temp_zipfiles(request)
    temp_directories = build_directories(request)
    cpplint_reports = []

    for zip_file, temp_directory in zip(zip_files, temp_directories):
        unzip_files(zip_file, temp_directory.name)
        os.chdir(temp_directory.name)
        report = run_cpplint('.')
        cpplint_reports.append(report)

    return '\n'.join(cpplint_reports)

def run_cpplint(directory):
    buf = StringIO()
    try:
        sh.cpplint("--recursive", directory, _err=buf)
    except sh.ErrorReturnCode_1 as e:
        pass
    return buf.getvalue()
