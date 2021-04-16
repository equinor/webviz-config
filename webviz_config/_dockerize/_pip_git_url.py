import warnings
from typing import Optional

import requests


def pip_git_url(
    version: str, source_url: str, git_pointer: Optional[str] = None
) -> str:
    """All webviz-config plugin projects are encouraged to be open source
    and on PyPI. Those that are not are encouraged to be on a git solution,
    and use quite standard setuptools_scm to give a runtime available version
    to the Python package.

    setuptool_scm enables us to get information regarding which hash/tag of the
    git repository to download + install in the Docker image, as installation from a
    clean repository state should give one of the following versions:

    no distance to tag:
        {tag}
    distance:
        {next_version}.dev{distance}+g{revision hash}

    If git_pointer argument is not None, this git ponter/reference is used instead
    of derived commit hash/tag from version.
    """

    source_url = source_url.rstrip("/")

    if git_pointer is None:
        git_pointer = version.split("+g")[1] if "+" in version else version

    if requests.get(source_url).status_code != 200:
        warnings.warn(
            f"Could not find {source_url}, assuming private repository. Changing to "
            "SSH URL. If building Docker image you will need to provide a deploy key."
        )
        for string in ["https://github.com/", "https://www.github.com/"]:
            source_url = source_url.replace(string, "ssh://git@github.com/")

    return f"git+{source_url}@{git_pointer}"
