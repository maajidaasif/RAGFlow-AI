from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

from .prompt import REPORT_PROMPT


class ReportGenerator:

    def __init__(self):

        # Model name
        self.model_name = "Qwen/Qwen2.5-3B-Instruct"

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name
        )

        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float32
        )

    def generate_report(
        self,
        literature_survey,
        comparison,
        research_gap
    ):

        # Create prompt
        prompt = f"""
{REPORT_PROMPT}

Literature Survey:
{literature_survey}

Paper Comparison:
{comparison}

Research Gap:
{research_gap}
"""

        # Convert text into tokens
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        )

        # Generate report
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.3,
                do_sample=True
            )

        # Decode tokens back to text
        report = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        return report