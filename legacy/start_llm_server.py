import json

from fastapi import FastAPI
import uvicorn

from legacy.api.payloads import GeneratePL
from legacy.llm.config import ModelConfig
from legacy.llm.ModelPipeline import ModelPipeline

config_path = 'ModelConfigs/llama_3_2_1B_instruct.json'
with open(config_path) as f:
    d = json.load(f)
    model_config = ModelConfig(**d)
llm = ModelPipeline(model_config)
llm.load_model()

app = FastAPI()


@app.post("/generate")
async def generate(pl: GeneratePL):
    """
    generate text with an LLM and a prompt given.
    """
    generated = llm.generate(pl.prompt)
    return {"generated": generated}


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
