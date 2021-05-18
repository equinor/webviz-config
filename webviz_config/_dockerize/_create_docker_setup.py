import os
import sys
import warnings
from pathlib import Path
from typing import Dict, Set

import jinja2
import requests

from ..plugins import PLUGIN_PROJECT_METADATA
from ._pip_git_url import pip_git_url


PYPI_URL_ROOT = "https://pypi.org/"


def create_docker_setup(
    build_directory: Path, plugin_metadata: Dict[str, dict]
) -> None:
    """Creates a Docker setup in build_directory. The input dictionary plugin_metadata
    is a dictionary of plugin metadata only for the plugins used in the generated
    application. This is used in order to automatically include the necessary
    plugin projects as Python requirements in the generated Docker setup.
    """

    template_environment = jinja2.Environment(  # nosec
        loader=jinja2.PackageLoader("webviz_config", "templates"),
        undefined=jinja2.StrictUndefined,
        autoescape=False,
    )
    template = template_environment.get_template("Dockerfile.jinja2")

    distributions = {
        metadata["dist_name"]: PLUGIN_PROJECT_METADATA[metadata["dist_name"]]
        for metadata in plugin_metadata.values()
    }

    # Regardless of a standard webviz-config plugin is included in user's
    # configuration file, we still need to install the plugin framework webviz-config:
    distributions["webviz-config"] = PLUGIN_PROJECT_METADATA["webviz-config"]

    requirements = get_python_requirements(distributions)
    requirements.add("gunicorn")

    (build_directory / "requirements.txt").write_text(
        "\n".join(sorted(list(requirements)))
    )

    (build_directory / "Dockerfile").write_text(
        template.render(
            {
                "python_version_major": sys.version_info.major,
                "python_version_minor": sys.version_info.minor,
                "ssh_required": any("ssh://" in req for req in requirements),
            }
        )
    )


def get_python_requirements(distributions: dict) -> Set[str]:

    requirements = set()

    for dist_name, dist in distributions.items():

        requirements.update(
            [
                f"{dep}=={version}"
                for dep, version in PLUGIN_PROJECT_METADATA[dist_name][
                    "dependencies"
                ].items()
                if dep not in distributions
            ]
        )

        if dist["download_url"] is None and dist["source_url"] is None:
            warnings.warn(
                f"Plugin distribution {dist_name} has no download/source URL specified. "
                "Will therefore not automatically become part of built Docker image."
            )
            continue

        if dist["download_url"] is not None and dist["download_url"].startswith(
            PYPI_URL_ROOT
        ):
            pypi_data = requests.get(f"{PYPI_URL_ROOT}/pypi/{dist_name}/json").json()
            if dist["dist_version"] in pypi_data["releases"]:
                requirements.add(f"{dist_name}=={dist['dist_version']}")
                continue

            if dist["source_url"] is None:
                raise RuntimeError(
                    f"Could not find version {dist['dist_version']} of {dist_name} on PyPI. "
                    "Falling back to git source code is not possible since "
                    "project_urls['Source'] is not defined in setup.py."
                )

        requirements.add(
            pip_git_url(
                dist["dist_version"],
                source_url=os.environ.get(
                    "SOURCE_URL_" + dist_name.upper().replace("-", "_"),
                    dist["source_url"],
                ),
                git_pointer=os.environ.get(
                    "GIT_POINTER_" + dist_name.upper().replace("-", "_")
                ),
            )
        )

    return requirements
