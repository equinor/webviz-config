from typing import Any, Generator

import pytest

from webviz_config.testing import WebvizComposite


@pytest.fixture
def _webviz_duo(request: Any, dash_thread_server: Any, tmpdir: Any) -> Generator:
    with WebvizComposite(
        dash_thread_server,
        browser=request.config.getoption("webdriver"),
        remote=request.config.getoption("remote"),
        remote_url=request.config.getoption("remote_url"),
        headless=request.config.getoption("headless"),
        options=request.config.hook.pytest_setup_options(),
        download_path=tmpdir.mkdir("download").strpath,
        percy_assets_root=request.config.getoption("percy_assets"),
        percy_finalize=request.config.getoption("nopercyfinalize"),
        pause=request.config.getoption("pause"),
    ) as duo:
        yield duo
