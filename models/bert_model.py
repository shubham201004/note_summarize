import os
from typing import Union, List, Dict, Any
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load .env file into environment variables
load_dotenv()

client = InferenceClient(api_key=os.getenv("HF_TOKEN"))

def text_summarization(input_text: str) -> str:
    response = client.summarization(
        text=input_text,
        model="google/pegasus-xsum",   # summarization model
        
    )

    # Hugging Face summarization returns dict with "summary_text"
    if isinstance(response, dict) and "summary_text" in response:
        return response["summary_text"]
    elif isinstance(response, list) and len(response) > 0 and "summary_text" in response[0]:
        return response[0]["summary_text"]
    elif isinstance(response, str):
        return response
    else:
        return "No summary generated."
