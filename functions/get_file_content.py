import os
from config import *
from google import genai
from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads file content for given file parameter, limited to 10,000 characters. Limited to working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file_path is a given filepath, where the file resides and can be read from.",
            ),
        },
    ),
)


def get_file_content(working_directory, file_path):
    relative_path = os.path.join(working_directory, file_path)
    if os.path.abspath(relative_path).startswith(os.path.abspath(working_directory)):
        try:
            if os.path.isfile(relative_path):
                with open(relative_path, "r") as f:
                    content = f.read()
                if len(content) > MAX_CHARS:
                    content = content[:MAX_CHARS] + f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
                return content
            else:
                return f'Error: File not found or is not a regular file "{file_path}"'
        except Exception as e:
            return f'Error: {e}'

    elif os.path.isfile(relative_path) == False:
        return f'Error: File not found or is not a regular file "{file_path}"'
    else:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        