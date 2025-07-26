import transformers
import torch

from src.llm.config import ModelConfig


class ModelPipeline:
    config: ModelConfig
    pipeline = None
    terminators = None

    def __init__(self, config: ModelConfig):
        """
        pipeline for a configuration for a LLM Model pipeline.
        :param config: configuration for the model pipeline
        """
        self.config = config
        self.terminators = None

    def load_model(self):
        self.pipeline = transformers.pipeline(
            "text-generation",
            model=self.config.model_path,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto",
        )
        self.terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

    def generate(self, prompt: str):
        messages = [
            {
                "role": "system",
                "content":
                    """
                    You are an helpful assistant.
                    """
            },
            {
                "role": "user",
                "content": f"""{prompt}"""
            },
        ]

        outputs = self.pipeline(
            # prompt,
            messages,
            max_new_tokens=1024,
            eos_token_id=self.terminators,
            do_sample=True,
            temperature=0.1,
            top_p=0.9,
        )
        # print(outputs)
        result = outputs[0]["generated_text"][-1]
        return result
