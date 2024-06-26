import textwrap

import develop_mode
import responses
import terminal_mode
from constants import TAB_SIZE


def load_help_cmd_info(command: str) -> str:
    space = ' ' * TAB_SIZE * 2
    path_to_txt = f"../data/txt/help_cmd_info/{command}.txt"

    with open(path_to_txt, 'r') as file:
        lines = file.readlines()

    information = space.join(lines)

    current_path = ''
    if responses.is_terminal_mode == True:
        current_path = terminal_mode.current_path()
    elif responses.is_develop_mode == True:
        current_path = develop_mode.current_path()
    return textwrap.dedent(
        f"""
        ```
        {information}
        ```
        ```
        {current_path}
        ```
        """
    )
