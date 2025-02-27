# views.py
import json

import google.generativeai as genai
from django.contrib.auth.decorators import login_required
from django.db import transaction  # Import transaction management
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from PIL import Image

# Import the Gemini functions
from .gemini_client import count_input_tokens, stream_gemini_completion
from .models import Chat, Message, MessageImage, UserProfile
from .utils import convert_image_to_webp

load_dotenv()

@login_required
def index(request):
    return render(request, "aichat/index.html")


@login_required
@csrf_exempt
def ask_gemini_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed."}, status=405)

    if request.content_type.startswith("application/json"):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)
        prompt = data.get("prompt", "")
        model_name = data.get("model", "models/gemini-2.0-flash-lite-preview-02-05")
        files = []
    else:
        prompt = request.POST.get("prompt", "")
        model_name = request.POST.get(
            "model", "models/gemini-2.0-flash-lite-preview-02-05"
        )
        files = request.FILES.getlist("images")

    user = request.user
    chat_id = request.POST.get("chat_id") or request.session.get("chat_id")

    try:
        if chat_id:
            chat = Chat.objects.get(id=chat_id, user=user)
        else:
            chat = Chat.objects.create(
                user=user, title=f"Chat with Gemini ({model_name})"
            )
        request.session["chat_id"] = chat.id
    except Chat.DoesNotExist:
        return JsonResponse({"error": "Chat not found."}, status=404)

    # Prepare contents for Gemini, including images as PIL objects.
    contents = [{"role": "user", "content": prompt}]
    images = []
    for file in files:
        try:
            img = Image.open(file)
            img.load()
            images.append(img)
            file.seek(0)  # Reset file pointer
        except Exception as e:
            print(f"Failed to open image: {e}")
            #  Return an error to the user.
            return JsonResponse({"error": f"Failed to process image: {e}"}, status=400)

    for img in images:
        contents.append({"role": "user", "content": img})

    try:
        # Get the user's profile and check token limits.
        user_profile = UserProfile.objects.get(user=user)
        model = genai.GenerativeModel(model_name)
        input_tokens = count_input_tokens(model, contents)

        if not user_profile.has_enough_tokens(input_tokens):
            return JsonResponse(
                {"error": "Not enough tokens to send request."}, status=403
            )
    except UserProfile.DoesNotExist:
        return JsonResponse(
            {"error": "UserProfile not found.  Contact support."}, status=500
        )
    except ValueError as e:  # Catch the custom exception
        return JsonResponse({"error": str(e)}, status=403)
    except Exception as e:
        return JsonResponse({"error": f"Token counting error: {e}"}, status=500)

    # Use a database transaction to ensure atomicity.
    with transaction.atomic():
        user_profile.reset_tokens_if_needed()  # Check for daily reset
        # Save user's prompt and consume input tokens.
        message = Message.objects.create(
            chat=chat,
            sender="user",
            content=prompt,
            tokens_consumed=input_tokens,
            user_profile=user_profile,  # Explicitly set user_profile
        )
        user_profile.consume_tokens(input_tokens)

        # Save images.
        for file in files:
            try:
                webp_image = convert_image_to_webp(file)
                MessageImage.objects.create(message=message, image=webp_image)
            except Exception as e:
                #  Log the error, but continue (don't block the entire request).
                print(f"Failed to process image: {e}")
                Message.objects.create(
                    chat=chat,
                    sender="system",
                    content=f"Failed to process image: {str(e)}",
                )

        # Stream and save AI response.
        def stream_and_save():
            full_reply = ""
            total_response_tokens = 0
            try:
                token_stream = stream_gemini_completion(contents, model_name=model_name)
                for token in token_stream:
                    full_reply += token
                    total_response_tokens += (
                        1  # We get response token one by one, increment by one.
                    )
                    yield token
            except Exception as e:
                error_message = f"Error: {str(e)}"
                full_reply += error_message
                yield error_message  # Important: yield the error to the frontend
            finally:
                # Save the complete AI response and update consumed tokens
                try:
                    with transaction.atomic():  # Nested transaction for the AI response
                        ai_message = Message.objects.create(
                            chat=chat,
                            sender="ai",
                            content=full_reply,
                            tokens_consumed=total_response_tokens,
                        )
                        user_profile.consume_tokens(total_response_tokens)
                except Exception as e:
                    print(f"Error saving AI response: {e}")

        return StreamingHttpResponse(stream_and_save(), content_type="text/plain")
