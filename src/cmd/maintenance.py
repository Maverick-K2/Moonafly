import responses
import develop_mode


from datetime import datetime
import textwrap
import re
import json


def set_maintenance(msg: str) -> str:

    # r_time = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')

    try:
        time = datetime.strptime(msg, '%Y-%m-%d %H:%M:%S')

        with open('../data/txt/init_files/maintenance.txt', 'w') as file:
            file.write('True\n' + str(time) + '\n' + responses.develop_mode_current_using_user)

        return textwrap.dedent(f"""
            ```
            maintenance set up successfully
            {develop_mode.current_path()}
            ```
        """)

    except ValueError:
        return textwrap.dedent(f"""
            ```
            you should follow this format
            YYYY:MM:DD hh:mm:ss
            {develop_mode.current_path()}
            ```
        """)
    