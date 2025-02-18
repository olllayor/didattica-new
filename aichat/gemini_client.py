# gemini_client.py
import os
from io import BytesIO
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
from .prompt import SYSTEM_PROMPT
from typing import List, Dict, Union

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)


def prepare_gemini_messages(messages):
    """Prepares messages for the Gemini API, handling text and images."""
    gemini_messages = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if isinstance(content, str):
            gemini_messages.append({"role": role, "parts": [content]})
        elif isinstance(content, Image.Image):
            gemini_messages.append({"role": role, "parts": [content]})
        else:
            gemini_messages.append({"role": role, "parts": [str(content)]})
    return gemini_messages


def count_input_tokens(
    model: genai.GenerativeModel, messages: List[Dict[str, Union[str, Image.Image]]]
) -> int:
    """Counts the tokens for the input messages, including images."""
    total_tokens = 0
    for message in messages:
        if isinstance(message["content"], str):
            response = model.count_tokens(message["content"])
            total_tokens += response.total_tokens
        elif isinstance(message["content"], Image.Image):
            #  Gemini API's count_tokens handles PIL Images directly.
            response = model.count_tokens(message["content"])
            total_tokens += response.total_tokens
        else:
            print("else")
    return total_tokens


def stream_gemini_completion(messages, model_name="models/gemini-2.0-flash-001"):
    """Streams the response from the Gemini API and yields tokens."""
    try:
        model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)
        gemini_messages = prepare_gemini_messages(messages)

        # Separate history and prompt.
        history = gemini_messages[:-1]
        prompt = gemini_messages[-1]["parts"][0]

        chat = model.start_chat(history=history)
        response = chat.send_message(prompt, stream=True)

        for chunk in response:
            yield chunk.text

    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        yield f"Error: {str(e)}"


