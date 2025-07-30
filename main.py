import os
from dotenv import load_dotenv
from google import genai
import sys
from functions.get_files_info import *
from google import genai
from google.genai import types
from functions.get_file_content import *
from functions.run_python_file import *
from functions.write_file import *

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
prompt = None
verbose_mode = False    

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

It is safe to explore the directories and gather information to answer questions or complete tasks. You're hard limited to the working directory, do not fear!
You must try all avenues with the information at hand before asking for more context.

When calling get_files_info:
- Call get_files_info with the "directory" parameter as a string. E.g. {"directory": "pkg"}

When calling get_file_content:
- Call get_file_content with the "file_path" parameter as a string. E.g. {"file_path": "main.py"}

When calling run_python_file:
- Call run_python_file with the "file_path" parameter as a string. E.g. {"file_path": "main.py"}

When calling write_file:
- Call write_file with two parameters:
    - "file_path": a string for the file's path
    - "content": a string containing the content to write  
  E.g. {"file_path": "main.txt", "content": "hello"}
All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file
    ]
)

def generate_content(messages):
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=messages,
        config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt
))
    return response


def call_function(function_call_part, verbose=False):
    function_call_part.args.update({"working_directory": "./calculator"})
    functions = {"write_file": write_file,
                 "get_file_content": get_file_content,
                 "run_python_file": run_python_file,
                 "get_files_info": get_files_info}
    if function_call_part.name not in functions:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
            name=function_call_part.name,
            response={"error": f"Unknown function: {function_call_part.name}"},
        )
    ],
)

    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    function_result = functions[function_call_part.name](**function_call_part.args)
    return types.Content(
    role="tool",
    parts=[
        types.Part.from_function_response(
            name=function_call_part.name,
            response={"result": function_result},
        )
    ],
)



def main():
    args = sys.argv[1:]
    prompt = None
    verbose_mode = False
    for i, arg in enumerate(args):
        if arg == "--verbose":
            verbose_mode = True
        elif not arg.startswith("--"):
            prompt = arg
    
    if prompt is None:
        print("Please provide a prompt.")
        sys.exit(1)
    
    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]
    i = 0
    while i < 20:
        try:
            response = generate_content(messages)
            for candidate in response.candidates:
                messages.append(candidate.content)
            if response.function_calls:
                for function_call_part in response.function_calls:
                    function_result = call_function(function_call_part, verbose_mode)
                    tool_output = function_result.parts[0].text
                    if not tool_output:
                        raise Exception("no response received")
                    if verbose_mode:
                        print(f"-> {tool_output}")
                    messages.append(function_result)
            i += 1
            if len(response.text) > 25:
                print(response.text)
                break;
        except Exception as e:
            print({e})
        

    if verbose_mode:   
        print("----------Verbose response----------")
        print(f'User prompt: {prompt}')
        print(f'Prompt tokens: {response.usage_metadata.prompt_token_count}')
        print(f'Response tokens: {response.usage_metadata.candidates_token_count}')
        
        

if __name__ == "__main__":
    main()
