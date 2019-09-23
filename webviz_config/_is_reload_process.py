import os

def is_reload_process():
    '''Within the flask reload machinery, it is not straight forward to know
    if the code is run as the main process (i.e. the process the user directly
    started), or if the code is a "hot reload process" (see Flask
    documentation).

    This utility function will use the fact that the reload process is started
    by the main process, and then utilize environment variables to tell which
    of the two actually runs.

    WARNING: For this function to work, it is essential that it is called in
    the main process (which for all practical use cases should be the case,
    since it is the same code that runs for both the main and reload process).

    Note that environment variables set dynamically are only seen by the
    running process and child processes (if any).
    '''

    if os.environ.get('WEBVIZ_MAIN_PID') == str(os.getppid()):
        reload_process = True
    else:
        os.environ[f'WEBVIZ_MAIN_PID'] = str(os.getpid())
        reload_process = False

    return reload_process
