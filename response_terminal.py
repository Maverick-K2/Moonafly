from math import *
import json
import random
import requests
from search_dict import search_dict
from search_weather import get_weather_info
from math_calc import safe_eval
import responses
import os
import re
import textwrap

# vocab_file = open('./json/vocabulary_items.json')
# vocab_list = json.load(vocab_file)['vocabularies']
# vocab_file.close()

directory_structure = []

def get_directory_structure():
    global directory_structure
    with open('./json/directory_structure.json') as directory_structure_file:
        directory_structure = json.load(directory_structure_file)['directory_structure']

def get_ls_command_output(files, tab_size, tab_count) -> str:
    output = ""
    columns = 3;
    column_len = [0] * columns
    for column_index in range(min(columns, len(files))):
        grouped_files = [file for index, file in enumerate(files) if index % columns == column_index]
        column_len[column_index] = max(len(file_name) for file_name in grouped_files)

    for index, file in enumerate(files):
        output += file + ' ' * (column_len[index % columns] - len(file) + 2 if index % columns != columns - 1 else 0)
        if index % columns == columns - 1 and index != len(files) - 1:
            output += '\n' + ' ' * tab_size * tab_count

    return output

path_stack = []

# generating the current working directory
def current_path() -> str:
    global path_stack
    path = "Moonafly:"
    for folder in path_stack:
        if folder != '~':
            path += '/'
        path += folder
    return path + "$"

def get_response_in_terminal_mode(message) -> str:
    username = str(message.author)
    msg = str(message.content)

    global path_stack

    # cd command
    if msg[:2] == 'cd':
        path = msg[2:].lstrip()
        
        # blank or ~ should go directly to ~
        if not path or path == '~':
            path_stack = ['~']
            return f"```{current_path()}```"
        
        # skip all the '\' and split the path into a folder list
        path = path.replace('\\', '').split('/')

        # go to the root directory
        if path[0] == '/':
            return textwrap.dedent(f"""\
                ```
                permission denied
                * this command requires the highest authority
                {current_path()}
                ```
            """)

        temporary_path_stack = path_stack[:]

        for folder in path:
            # if the folder is empty or . then nothing happens with the 
            if folder == '' or folder == '.':
                continue

            # move up one directory 
            elif folder == '..':
                if len(temporary_path_stack) > 1:
                    temporary_path_stack.pop()
                elif temporary_path_stack[0] == '~':
                    return textwrap.dedent(f"""\
                        ```
                        bash: cd: {msg[2:].lstrip()}: No such file or directory
                        {current_path()}
                        ```
                    """)

            else:
                temporary_path_stack.append(folder)

        current_directory = directory_structure
        for folder in temporary_path_stack:
            if folder in list(current_directory):
                current_directory = current_directory[folder]
            else:
                return textwrap.dedent(f"""\
                    ```
                    bash: cd: {msg[2:].lstrip()}: No such file or directory
                    {current_path()}
                    ```
                """)
        
        path_stack = temporary_path_stack
        return f"```{current_path()}```"

    # ls command
    elif msg[:2] == 'ls':
        get_directory_structure()
        current_directory = directory_structure
        for folder in path_stack:
            current_directory = current_directory[folder]

        files_in_current_directory = sorted(list(current_directory))

        return textwrap.dedent(f"""\
            ```
            {get_ls_command_output(files_in_current_directory, 4, 3)}
            {current_path()}
            ```
        """)

    # return the full pathname of the current working directory
    elif msg[:3] == 'pwd':
        # delete the prefix 'Moonafly:' and the suffix '$'
        path = current_path()[9:-1]
        # delete the prefix no matter it is '~' or '/' path_stack still has the data
        path = path[1:]

        if path_stack[0] == '~':
            path = 'home/Moonafly' + path 

        return textwrap.dedent(f"""\
            ```
            /{path}
            {current_path()}
            ```
        """)
    
    # commands in certain directory
    if path_stack[-1] == 'math':
        # if username not in responses.special_guests:
        #     return 'permission denied'
        return safe_eval(msg)

    elif path_stack[-2] == 'gen':
        if path_stack[-1] == 'vocab':
            if msg == 'get':
                return "sorry, still developing"
                return list[random.randint(0, len(list))]

        # my generators repo on github.io
        elif path_stack[-1] == 'fortune':
            if msg == 'get':
                return 'https://lifeadventurer.github.io/generators/fortune_generator' 

        else:
            return 'no such command' 
    
    elif path_stack[-2] == 'search':
        # search for a handle in different online judges
        if path_stack[-1] == 'oj':
            pattern = r'-(\d+)\s+(\w+)'
            match = re.search(pattern, msg)
            if match:
                number = int(match.group(1))
                handle = match.group(2)
                url = ""
                # TODO: make this as a file or at least a list
                if number == 1:
                    url = "https://atcoder.jp/users/"
                elif number == 2:
                    url = "https://www.codechef.com/users/"
                elif number == 3:
                    url = "https://codeforces.com/profile/"
                elif number == 4:
                    url = "https://csacademy.com/user/"
                elif number == 5:
                    url = "https://dmoj.ca/user/"
                elif number == 6:
                    url = "https://leetcode.com/"
                elif number == 7:
                    url = "https://profiles.topcoder.com/"
                else:
                    return 'please enter a valid number'

                url += handle
                response = requests.get(url)
                if response.status_code == 404:
                    return f"The handle {handle} is not found"
                else:
                    return url

            else:
                return 'please type the right command format, using help to see what are the available options'

        # just a google search -> must improve this more
        elif path_stack[-1] == 'google':
            return "https://www.google.com/search?q=" + msg

        # same as above -> need improvement
        elif path_stack[-1] == 'youtube':
            return "https://www.youtube.com/results?search_query=" + msg

        # search for github repos or profiles -> because url
        elif path_stack[-1] == 'github':
            github_url = "https://github.com/" + msg
            response = requests.get(github_url)
            if response.status_code == 404:
                return f"The url {github_url} is not found (404 Not Found)."
            else:
                return github_url

        # search for git commands
        elif path_stack[-1] == 'git':
            # msg = msg[4:]
            # if msg[:2] == 'ls':
            #     return textwrap.dedent(f"""\
            #         ```
            #         setup              -1
            #         init               -2
            #         stage & snapshot   -3  
            #         branch & merge     -4
            #         inspect & compare  -5
            #         share & update     -6
            #         {current_path()}
            #         ```
            #     """)

            # pattern = r'-(\d+)\s+(\w+)'
            # match = re.search(pattern, msg)
            # if match:
            #     number = int(match.group(1))
            #     command = match.group(2)

            # msg = msg[1:]
            # if msg > '6' or msg < '1':
            #     return 'no such command'
            # else:
                return 'sorry, this function is still developing'
            # TO-DO
            # elif msg == 'setup':

        elif path_stack[-1] == 'greek':
            if msg == 'get':
                return textwrap.dedent(f"""\
                    ```
                    Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω
                    α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω
                    {current_path()}
                    ```
                """)

        else:
            return 'no such command'
    
    elif path_stack[-1] == 'weather':
        if msg == 'get':
            return textwrap.dedent(f"""\
                ```
                {get_weather_info()}
                {current_path()}
                ```
            """)

    # roll a random number
    elif path_stack[-1] == 'roll':
        if not all(char.isdigit() for char in msg):
            return 'please enter a valid number'
        else:
            return random.randint(1, int(msg))

    # return the definition and example of the enter word from a dictionary
    elif path_stack[-1] == 'dict':
        match = re.search(r'(\w+)\s+LIMIT\s+(\d+)', msg)
        if match:
            return search_dict(match.group(1), int(match.group(2)))
        elif 'LIMIT' in msg:
            return 'please type a number after the command LIMIT'
        else:
            return textwrap.dedent(f"""
                ```
                {search_dict(msg, 3)}
                {current_path()}
                ```
            """)

    else:
        return 'no such command'