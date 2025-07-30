import os
from google import genai
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes data to a given file, given a string value, constrained to working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The filepath to write the given file at. Will be created if it doesn't yet exist.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to be written to the file passed through the function"
            ),
        },
    ),
)


def write_file(working_directory, file_path, content):
    relative_path = os.path.join(working_directory, file_path)
    if os.path.abspath(relative_path).startswith(os.path.abspath(working_directory)):
        try:
            if os.path.exists(relative_path):
                with open(relative_path, "w") as f:
                    f.write(content)
                return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
                    
            else:
                file_dir = os.path.dirname(relative_path)
                if os.path.exists(file_dir):
                    with open(relative_path, "w") as f:
                        f.write(content)
                else:
                    os.makedirs(file_dir)
                    with open(relative_path, "w") as f:
                        f.write(content)
                return f'Successfully created parent directories and wrote to "{file_path}" ({len(content)} characters written)'
            
        except Exception as e:
            return f'Error: {e}'

    else:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'