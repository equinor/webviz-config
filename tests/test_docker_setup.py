import pytest

from webviz_config._dockerize._create_docker_setup import get_python_requirements


@pytest.mark.parametrize(
    "distributions, requirements",
    [
        (
            {
                "webviz-config": {
                    "download_url": "https://pypi.org/project/webviz-config",
                    "source_url": None,
                    "dist_version": "0.3.0",
                }
            },
            ["webviz-config==0.3.0"],
        ),
        (
            {
                "webviz-config": {
                    "download_url": None,
                    "source_url": None,
                    "dist_version": "0.3.0",
                }
            },
            [],
        ),
        (
            {
                "webviz-config": {
                    "download_url": None,
                    "source_url": "https://github.com/equinor/webviz-config",
                    "dist_version": "0.3.0",
                }
            },
            ["git+https://github.com/equinor/webviz-config@0.3.0"],
        ),
    ],
)
def test_derived_requirements(distributions, requirements):
    with pytest.warns(None) as record:
        assert set(requirements).issubset(get_python_requirements(distributions))
        assert len(record) == len(
            [
                metadata
                for metadata in distributions.values()
                if metadata["download_url"] is None and metadata["source_url"] is None
            ]
        )
