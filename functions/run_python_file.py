import os
import subprocess
from google import genai
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs ONLY python files, checks for '.py' filetype, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The filepath to run the given python file at. Python3 is pre-added, so it isn't needed.",
            ),
        },
    ),
)

def run_python_file(working_directory, file_path, args=[]):
    relative_path = os.path.join(working_directory, file_path)
    if os.path.abspath(relative_path).startswith(os.path.abspath(working_directory)):
        try:
            if os.path.exists(relative_path):
                if file_path.endswith(".py"):
                    command = ["python3", file_path] + args
                    completed_process = subprocess.run(command, capture_output=True, text=True, cwd=working_directory, timeout=30)
                    stdout_text = completed_process.stdout
                    stderr_text = completed_process.stderr
                    exit_code = completed_process.returncode
                    output = f"STDOUT: {stdout_text} STDERR: {stderr_text}"

                    if exit_code != 0:
                        output += f"Process exited with code {exit_code}"

                    if not stdout_text and not stderr_text:
                        return "No output produced."

                    return output
                else:
                    f'Error: "{file_path}" is not a Python file.'
            else:
                return f'Error: File "{file_path}" not found.'
            
        except Exception as e:
            return f'Error: executing python file: {e}'

    else:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'