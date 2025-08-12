import json

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

from legacy.llm.config import ModelConfig


class ModelPipeline:
    config: ModelConfig
    pipeline = None
    terminators = None
    model = None
    tokenizer = None

    def __init__(self, config: ModelConfig):
        """
        pipeline for a configuration for a LLM Model pipeline.
        :param config: configuration for the model pipeline
        """
        self.config = config
        self.terminators = None

    def load_model(self):
        self.pipeline = None
        # self.pipeline = transformers.pipeline(
            # "text-generation",
            # model=self.config.model_path,
            # model_kwargs={"torch_dtype": torch.bfloat16},
            # device_map="auto",
        # )

        self.model = AutoModelForCausalLM.from_pretrained(self.config.model_path, device_map="cuda", torch_dtype=torch.bfloat16)
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_path)

        self.terminators = [
            self.tokenizer.eos_token_id,
            self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

    def generate(self, prompt: str):
        messages = [
            {
                "role": "system",
                "content":
                    """
                    You are an helpful assistant. YOU HAVE TO RESPOND IN JSON FORMAT.
                    The schema is defined by the tools.
                    """
            },
            {
                "role": "user",
                "content": f"""{prompt}"""
            },
        ]

        tools = [{
          "name": "get_weather",
          "description": "Gets the current weather information for a specific location.",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {
                "type": "string",
                "description": "The name of the city or location to get the weather for, e.g., 'San Francisco' or 'Tokyo'."
              },
              "units": {
                "type": "string",
                "enum": ["metric", "imperial"],
                "description": "The unit system to use for temperature and wind speed. 'metric' for Celsius, 'imperial' for Fahrenheit."
              }
            },
            "required": ["location"]
          }
        }]

        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            tools=tools,
        ).to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=40)
        result = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:])
        print(self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:]))
        tmp = json.loads(result)
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
