import os
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to execute, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING
                ),
                description="Arguments to pass to the Python file",
            ),
        },
    ),
)
def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
        #path validation: check if the file is within the working directory
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
        if not valid_target_file:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
    except Exception as e:
        return f"Error: {str(e)}"

        #subprocess execution
    try:
        command = ["python", target_file]
        if args:
            command.extend(args)
        completed_process = subprocess.run(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        if completed_process.returncode != 0:
            return f'Process exited with code {completed_process.returncode}'
        if completed_process.stdout == "" and completed_process.stderr == "":
            return "No output produced"
        else:
            return f"STDOUT:{completed_process.stdout} STDERR:{completed_process.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"
        