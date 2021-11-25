import json
import shutil
import tempfile
import subprocess
from pathlib import Path


def binary_available() -> bool:
    """Returns True if the GitHub CLI binary (gh) is
    availabile in $PATH, otherwise returns False.
    """
    return shutil.which("gh") is not None


def logged_in() -> bool:
    # pylint: disable=subprocess-run-check
    result = subprocess.run(
        ["gh", "auth", "status"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # capture_output=True, <-- Added in Python 3.7
    )
    return b"Logged in to github.com" in result.stderr


def log_in() -> None:
    # pylint: disable=subprocess-run-check
    subprocess.run(
        ["gh", "auth", "login"],
    )


def repo_exists(github_slug: str) -> bool:
    # pylint: disable=subprocess-run-check
    result = subprocess.run(
        ["gh", "repo", "view", github_slug],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # capture_output=True <-- Added in Python 3.7
    )

    if not result.stderr:
        return True
    if b"Could not resolve" in result.stderr:
        return False
    raise RuntimeError(result.stderr)


def create_github_repository(github_slug: str, directory: Path) -> Path:
    """Creates a new private github repository. github_slug is on format
    owner/reponame.
    """
    if not "/" in github_slug:
        raise ValueError("repo_path argument should be on format owner/reponame")

    subprocess.run(
        ["gh", "repo", "create", github_slug, "--private", "--confirm"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # capture_output=True,  <-- Added in Python 3.7
        check=True,
        cwd=directory,
    )

    return directory / github_slug.split("/")[1]


def turn_on_github_vulnerability_alers(directory: Path) -> None:
    subprocess.run(
        [
            "gh",
            "api",
            "repos/:owner/:repo/vulnerability-alerts",
            "--method",
            "PUT",
            "--header",
            "Accept: application/vnd.github.dorian-preview+json",
        ],
        check=True,
        cwd=directory,
    )


def _call_post_api(endpoint: str, data: dict, directory: Path) -> None:
    subprocess.run(
        [
            "gh",
            "api",
            endpoint,
            "--method",
            "POST",
            "--input",
            "-",
            "--silent",
        ],
        input=json.dumps(data),
        check=True,
        cwd=directory,
        text=True,
    )


def add_webhook(directory: Path, receiver_url: str, secret: str) -> None:
    data = {
        "name": "web",
        "active": True,
        "config": {
            "url": receiver_url,
            "content_type": "json",
            "secret": secret,
        },
    }
    _call_post_api(data=data, endpoint="repos/:owner/:repo/hooks", directory=directory)


def add_deploy_key(directory: Path, title: str, key: str) -> None:
    _call_post_api(
        data={"title": title, "key": key},
        endpoint="repos/:owner/:repo/keys",
        directory=directory,
    )


def read_file_in_repository(github_slug: str, filename: str) -> str:
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_dir = Path(tmp_dir)
        subprocess.run(
            ["git", "clone", f"git@github.com:{github_slug}"],
            check=True,
            cwd=temp_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            # capture_output=True,  <-- Added in Python 3.7
        )
        clone_path = temp_dir / github_slug.split("/")[1]

        return (clone_path / Path(filename)).read_text()


def commit_portable_webviz(
    github_slug: str,
    source_directory: Path,
    commit_message: str = "Initial commit",
    branch_name: str = "main",
) -> None:

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_dir = Path(tmp_dir)
        subprocess.run(
            ["git", "clone", f"git@github.com:{github_slug}"],
            check=True,
            cwd=temp_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        clone_path = temp_dir / github_slug.split("/")[1]

        shutil.copytree(
            source_directory,
            clone_path,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("resources"),
        )

        commands = [
            ["git", "add", "."],
            ["git", "commit", "-m", commit_message, "--allow-empty"],
            ["git", "branch", "-M", branch_name],
            ["git", "push", "-u", "origin", branch_name],
        ]
        for command in commands:
            subprocess.run(
                command,
                check=True,
                cwd=clone_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
