import os
import re
from typing import List, Callable, Optional

from webviz_config.utils import terminal_colors


def terminal_title(title: str) -> None:
    print("\n" + terminal_colors.BOLD + title + terminal_colors.END)
    print("=" * len(title) + "\n")


def terminal_yes_no(question: str) -> bool:
    while True:
        reply = input(question + " (y/n): ").lower().strip()
        if reply.startswith("y"):
            return True
        if reply.startswith("n"):
            return False


def terminal_list_selector(options: List[str], display_string: str) -> str:

    for i, subscription in enumerate(options):
        print(f"{i+1}) {subscription}")
    print()

    selected_value = None
    while selected_value not in options:
        try:
            index = int(input(f"Choose {display_string} index to use: "))
            return_value = selected_value = options[index - 1]
        except (IndexError, ValueError):
            print(f"Select an integer in range 1-{len(options)}.")

    print(
        "\n"
        + terminal_colors.BOLD
        + f"Selected {display_string}: {selected_value}"
        + terminal_colors.END
    )
    return return_value


def user_input_from_stdin(env_var: str, noun: str, regex: str = None) -> str:
    if env_var in os.environ:
        value = os.environ[env_var]
        print(f"Using {noun} '{value}' (from environment variable {env_var}).")
        if regex is not None and not re.fullmatch(regex, value):
            raise RuntimeError("Input not on expected format.")
        return value

    print(f"Tip: Default value can be set through env. variable {env_var}\n")
    while True:
        value = input(f"{noun.capitalize()}: ").strip()
        if regex is None or re.fullmatch(regex, value):
            return value
        print("Input not on expected format.")


def user_input_from_list(env_var: str, noun: str, choices: List[str]) -> str:
    if env_var in os.environ:
        value = os.environ[env_var]
        print(f"Using {noun} '{value}' (from environment variable {env_var}).")
        if value not in choices:
            raise ValueError(
                f"Value '{value}' not among available choices ({', '.join(choices)})"
            )
        return value

    print(f"Tip: Default value can be set through env. variable {env_var}\n")
    return terminal_list_selector(choices, noun)


def user_input_optional_reuse(
    env_var: str,
    noun: str,
    exists_function: Callable,
    reuse_allowed: bool = True,
    regex: Optional[str] = None,
) -> str:
    if env_var in os.environ:
        value = os.environ[env_var]
        print(f"Using {noun} '{value}' (from environment variable {env_var}).")
        if not reuse_allowed and exists_function(value):
            raise RuntimeError(f"There already exists an {noun} with name '{value}'.")
        if regex is not None and not re.match(regex, value):
            raise RuntimeError(
                f"Value {value} does not satisfy regular expression {regex}"
            )
        return value

    print(f"Tip: Default value can be set through env. variable {env_var}\n")

    while True:
        value = input(f"{noun.capitalize()}: ")

        if regex is not None and not re.match(regex, value):
            print(f"Value {value} does not satisfy regular expression {regex}")
            continue

        check = exists_function(value)

        if isinstance(check, tuple):
            exists, message = check
        else:
            exists = check
            message = None

        if exists:
            if not reuse_allowed:
                print(
                    f"There already exists an {noun} with name '{value}'"
                    if message is None
                    else message
                )
                continue
            print(f"Found existing {noun} with value '{value}'")
            reuse = terminal_yes_no(f"Do you want to reuse the existing {noun}")
            if reuse:
                return value
            continue

        print(f"{noun.capitalize()} name '{value}' is available.")
        return value
