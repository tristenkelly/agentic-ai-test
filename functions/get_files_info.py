import os
from google import genai
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

def get_files_info(working_directory, directory="."):
    relative_path = os.path.join(working_directory, directory)
    lines = []
    if os.path.isdir(relative_path) == False:
        return f'Error: "{directory}" is not a directory'
    elif os.path.abspath(relative_path).startswith(os.path.abspath(working_directory)):
        new_list = os.listdir(relative_path)
        for item in new_list:
            fullpath = os.path.join(relative_path, item)
            isitem = os.path.isfile(fullpath)
            size = os.path.getsize(fullpath)
            isdir = os.path.isdir(fullpath)
            item_string = f'- {item}: file_size={size} bytes, is_dir={isdir}'
            lines.append(item_string)
        return "\n".join(lines)
    else:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        