# Google Gemini API Integration for Exam Prep Project

This document outlines how to integrate the Google Gemini API (specifically the Gemini 2.0 Flash Experimental model) into your student exam preparation platform. It focuses on understanding posts containing both text and images, providing explanations, and generating solutions.

## Overview

Your project requires processing user posts (similar to tweets) that can include:

1.  **Textual Content:** The actual question or topic.
2.  **Image Content:**  Supporting images, diagrams, charts, etc.

The goal is to leverage Gemini's multimodal capabilities to:

*   **Understand:**  Analyze the text and images together to grasp the question/topic.
*   **Explain:**  Provide a clear explanation of the concepts involved.
*   **Solve:** Offer a solution or answer to the question/problem.

We'll be using the Gemini 2.0 Flash Experimental model via its API, focusing on efficient responses using streaming.

## API Setup and Authentication

1.  **Google Cloud Project:** You need a Google Cloud project with the Gemini API enabled.
2.  **API Key:** Obtain an API key from the Google Cloud Console. This key will be used for authentication.
3.  **Client Library:** Use an appropriate client library for your programming language (e.g., Python, Node.js, Java). We will assume Python with the `google-generativeai` library for the examples.

    ```python
    import google.generativeai as genai
    from google.generativeai.types import Part, Content

    genai.configure(api_key="YOUR_API_KEY") # Replace with your actual API key
    model = genai.GenerativeModel('gemini-2.0-flash-experimental')
    ```

## Constructing the Prompt

A good prompt is essential for getting the desired response from Gemini. Here’s a breakdown of how to construct your prompt, considering both text and image inputs:

### 1. Multimodal Input

Gemini's API allows you to pass both text and image data. You’ll structure your request using `Part` objects in the request content.

```python
def create_prompt_content(text_content, image_content=None):
    content = []

    # Add the text part
    if text_content:
        content.append(Part.from_text(text_content))
        
    # Add the image part, if available
    if image_content:
        if isinstance(image_content, list):  # Handle multiple images
          for img_bytes in image_content:
            content.append(Part.from_data(data=img_bytes, mime_type='image/jpeg')) 
        else:
          content.append(Part.from_data(data=image_content, mime_type='image/jpeg'))


    return [Content(parts=content)]

# Example usage:
# For single image 
with open("image1.jpg", "rb") as image_file:
  image_data = image_file.read()

# for multiple images
with open("image1.jpg", "rb") as image_file:
  image_data1 = image_file.read()
with open("image2.jpg", "rb") as image_file2:
  image_data2 = image_file2.read()
 
multiple_images = [image_data1,image_data2]

text = "Explain this physics problem and show the solution: A car accelerates from rest at 2 m/s^2 for 5 seconds."
content_single_image = create_prompt_content(text_content=text, image_content=image_data)
content_multiple_images = create_prompt_content(text_content=text, image_content=multiple_images)
content_text_only = create_prompt_content(text_content=text)
Use code with caution.
Markdown
2. Instructions within the Prompt
Clearly instruct Gemini on what you expect:

Context Setting: Start by mentioning the role and purpose of the request. For example, “You are an AI tutor helping students prepare for exams.”

Action: Explicitly request explanation, and solution. For example, “First, provide a clear explanation of the problem, then provide a step-by-step solution.”

Format: Request a structured output (if needed), like "Use bullet points" or "Format the solution using mathematical notation."

Example Prompt Structure:

"You are an AI tutor helping students prepare for exams. You will receive a question along with any related images. First, analyze the question along with any images, and then provide an explanation of the concepts involved. Finally, provide a step-by-step solution. Use clear and simple language, suitable for students. Make sure each step of solution is clear and use mathematical notation whenever necessary."
Use code with caution.
Complete Python Example with Full Prompt Construction:

import google.generativeai as genai
from google.generativeai.types import Part, Content


genai.configure(api_key="YOUR_API_KEY") # Replace with your actual API key
model = genai.GenerativeModel('gemini-2.0-flash-experimental')


def create_prompt_content(text_content, image_content=None):
    content = []

    # Add the text part
    if text_content:
        content.append(Part.from_text(text_content))
        
    # Add the image part, if available
    if image_content:
        if isinstance(image_content, list):  # Handle multiple images
          for img_bytes in image_content:
            content.append(Part.from_data(data=img_bytes, mime_type='image/jpeg')) 
        else:
          content.append(Part.from_data(data=image_content, mime_type='image/jpeg'))


    return [Content(parts=content)]

def get_gemini_response(text_content, image_content=None):

    prompt = """You are an AI tutor helping students prepare for exams. 
              You will receive a question along with any related images. 
              First, analyze the question along with any images, and then provide an explanation of the concepts involved. 
              Finally, provide a step-by-step solution. 
              Use clear and simple language, suitable for students. 
              Make sure each step of solution is clear and use mathematical notation whenever necessary."""

    content_with_prompt = create_prompt_content(text_content=prompt, image_content=image_content) 
    if text_content:
        content_with_prompt[0].parts.extend(create_prompt_content(text_content=text_content)[0].parts)


    response_stream = model.generate_content(
        content_with_prompt,
        stream=True
    )

    for chunk in response_stream:
        print(chunk.text, end="", flush=True)
    print("\n")



# Example Usage:
# For single image 
with open("image1.jpg", "rb") as image_file:
  image_data = image_file.read()

# for multiple images
with open("image1.jpg", "rb") as image_file:
  image_data1 = image_file.read()
with open("image2.jpg", "rb") as image_file2:
  image_data2 = image_file2.read()
 
multiple_images = [image_data1,image_data2]


text = "Explain this physics problem and show the solution: A car accelerates from rest at 2 m/s^2 for 5 seconds."
get_gemini_response(text_content=text, image_content=image_data)
print("===================================")
get_gemini_response(text_content=text, image_content=multiple_images)
print("===================================")
get_gemini_response(text_content=text)
Use code with caution.
Python
Using Streaming Tokens
Streaming lets you get responses from the model as they're being generated, instead of waiting for the entire answer. This significantly improves the user experience, as content is displayed faster.

The generate_content function's stream=True argument enables streaming. The response will be a generator, yielding parts of the response:

response_stream = model.generate_content(
        content_with_prompt,
        stream=True
    )
    for chunk in response_stream:
       print(chunk.text, end="", flush=True)
    print("\n")