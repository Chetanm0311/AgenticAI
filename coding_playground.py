import gradio as gr
import ast
import io
import sys

from code_generator import CodeGenerator
from msal_auth import Geni
geni = Geni()
code_gen = CodeGenerator(geni)
def extract_input_prompts(code):
    prompts = []
    class InputVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if getattr(node.func, "id", None) == "input":
                if node.args and isinstance(node.args[0], ast.Constant):
                    prompts.append(str(node.args[0].value))
                else:
                    prompts.append("")
            self.generic_visit(node)
    try:
        InputVisitor().visit(ast.parse(code))
    except Exception:
        pass
    return prompts

def run_user_code(code, *inputs):
    input_iter = iter(inputs)
    def fake_input(prompt=""):
        try:
            return next(input_iter)
        except StopIteration:
            return ""
    local_vars = {}
    try:
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        exec(code, {"input": fake_input}, local_vars)
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        return output, ""
    except Exception as e:
        sys.stdout = old_stdout
        return "", f"{type(e).__name__}: {e}"

with gr.Blocks() as demo:
    gr.Markdown("# Prompt → Python Code → Code Inputs → Output")

    user_prompt = gr.Textbox(label="Your Task (Describe in English)")
    gen_btn = gr.Button("Generate Python Code")
    code_display = gr.Code(label="Generated Python Code", language="python")
    gen_btn.click(lambda prompt: code_gen.generate_code(prompt), inputs=user_prompt, outputs=code_display)

    detect_btn = gr.Button("Detect & Show code input() fields")
    # Take a maximum of 5 input() fields:
    in1 = gr.Textbox(label="Input 1", visible=False)
    in2 = gr.Textbox(label="Input 2", visible=False)
    in3 = gr.Textbox(label="Input 3", visible=False)
    in4 = gr.Textbox(label="Input 4", visible=False)
    in5 = gr.Textbox(label="Input 5", visible=False)

    output = gr.Textbox(label="Output")
    error = gr.Textbox(label="Error")

    def show_boxes(code):
        prompts = extract_input_prompts(code)
        visibles = [gr.update(visible=True, label=p or f"Input {i+1}") if i < len(prompts) else gr.update(visible=False) for i, p in enumerate([""]*5)]
        for i, prompt in enumerate(prompts):
            visibles[i] = gr.update(visible=True, label=prompt or f"Input {i+1}")
        # Always return length 5!
        while len(visibles) < 5:
            visibles.append(gr.update(visible=False))
        return tuple(visibles[:5])

    detect_btn.click(
        show_boxes,
        inputs=code_display,
        outputs=[in1, in2, in3, in4, in5]
    )

    run_btn = gr.Button("Run Code")
    run_btn.click(
        run_user_code,
        inputs=[code_display, in1, in2, in3, in4, in5],
        outputs=[output, error]
    )

demo.launch()

