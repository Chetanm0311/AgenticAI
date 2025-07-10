import subprocess
import os
class CodeGenerator:
    system_prompt = """You are a code generation assistant.\n
                    Given a user's request, output only the relevant code in the language specified by the user.\n
                    Do not include explanations, comments, or markdown formatting—output only the raw code necessary to accomplish the user's task in the appropriate language.\n
                    Always ensure the output is a complete, executable code snippet unless otherwise instructed."""
    def __init__(self,model):
        self.model=model
    
    def generate_code(self,user_prompt,system_prompt=None):
        if not system_prompt:
            system_prompt = self.system_prompt
         
        response = self.model.chat(
            chat_msg=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}]
        )
        print(response.text)
        return response.text

    def clean_code(self,code):
        lines = code.splitlines()
        cleaned = [line for line in lines if not line.strip().startswith('```')]
        return '\n'.join(cleaned)
        
    def run_generated_code(self,code, filename="generated.py"):
        # Save code to file
        venv_path = os.environ.get("venv")
        if not venv_path:
            raise EnvironmentError("The 'venv' environment variable is not set.")
        code = self.clean_code(code)
        with open(filename, "w") as f:
            f.write(code)
        
        # Build python path for venv
        python_executable = os.path.join(venv_path, "bin", "python")  # Unix/MacOS
        if not os.path.exists(python_executable):  # Windows fallback
            python_executable = os.path.join(venv_path, "Scripts", "python.exe")

        # Run script and capture result/output
        try:
            # For graphviz-based output, the Python code itself will generate 'output.png'
            result = subprocess.run([python_executable, filename], capture_output=True, text=True, check=True)
            output = result.stdout
            error = result.stderr
        except subprocess.CalledProcessError as e:
            print("Running generated code failed:\n", e.stderr)
            output = ""
            error = e.error
        finally:
            os.remove(filename)  # Cleanup script file
        return output,error

