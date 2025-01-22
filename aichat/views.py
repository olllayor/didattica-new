import base64
import json
import os

import httpx
import PIL.Image
from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from google.generativeai import GenerativeModel, configure
from google.generativeai.types import Content, Part

from community.models import Post

from .models import AIModel, Conversation, Message, UserAPIToken

configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))


@sync_to_async
def get_gemini_response(model, prompt, image=None):
    try:
        # Configure model with optimal settings from documentation
        model_config = {
            "model": "gemini-1.5-pro",
            "generation_config": {
                "temperature": 0.9,
                "top_p": 1,
                "top_k": 40,
                "max_output_tokens": 2048,
            },
            "safety_settings": {
                "HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
                "HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
                "SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
                "DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
            },
        }

        genai_model = GenerativeModel(**model_config)
        chat = genai_model.start_chat(history=[])

        # Create prompt content based on documentation
        content = []
        base_prompt = (
            "You are an AI tutor helping students prepare for exams. "
            "Analyze the question along with any images, provide an explanation "
            "of the concepts involved, and give a step-by-step solution. "
            "Use clear and simple language, suitable for students."
        )
        content.append(Part.from_text(f"{base_prompt}\n\n{prompt}"))

        if image:
            if isinstance(image, str) and image.startswith("http"):
                response = httpx.get(image)
                image_data = {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(response.content).decode("utf-8"),
                }
                content.append(Part.from_data(**image_data))
            else:
                pil_image = PIL.Image.open(image)
                content.append(Part.from_data(pil_image))

        # Generate response with streaming
        response = chat.send_message(Content(parts=content), stream=True)

        # Collect streamed response
        full_response = []
        for chunk in response:
            if chunk.text:
                full_response.append(chunk.text)

        return "".join(full_response)

    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return "I apologize, but I encountered an error. Please try again."


@login_required
def chat_view(request):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "aichat/chat-modal.html")

    selected_ai = AIModel.objects.filter(is_active=True).first()
    ai_models = AIModel.objects.filter(is_active=True)

    # Get user's conversations with pagination
    conversations = Conversation.objects.filter(
        user=request.user, is_active=True
    ).select_related("ai_model")

    paginator = Paginator(conversations, 10)
    page = request.GET.get("page")
    conversations = paginator.get_page(page)

    user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
    is_mobile = any(
        device in user_agent for device in ["mobile", "android", "iphone", "ipad"]
    )

    return render(
        request,
        "aichat/chat_home.html",
        {
            "selected_ai": selected_ai,
            "ai_models": ai_models,
            "conversations": conversations,
            "is_mobile": is_mobile,
        },
    )


@login_required
def chat_conversation_view(request, conversation_id=None):
    selected_ai = AIModel.objects.filter(is_active=True).first()
    ai_models = AIModel.objects.filter(is_active=True)

    if conversation_id:
        conversation = get_object_or_404(
            Conversation.objects.prefetch_related("messages"),
            id=conversation_id,
            user=request.user,
        )
        messages = conversation.messages.all()
    else:
        conversation = None
        messages = []

    if request.method == "POST":
        message_content = request.POST.get("message", "")
        ai_model_id = request.POST.get("model", "")

        if not conversation:
            # Create new conversation
            selected_ai = AIModel.objects.get(model_id=ai_model_id)
            conversation = Conversation.objects.create(
                user=request.user, ai_model=selected_ai
            )

        if message_content:
            # Save user message
            user_message = Message.objects.create(
                conversation=conversation, content=message_content, is_user=True
            )

            # Get AI response
            ai_response = get_gemini_response(ai_model_id, message_content)

            # Save AI response
            ai_message = Message.objects.create(
                conversation=conversation, content=ai_response, is_user=False
            )

            # Update conversation title if it's the first message
            if not conversation.title:
                conversation.update_title_from_first_message()

            messages = conversation.messages.all()

    user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
    is_mobile = any(
        device in user_agent for device in ["mobile", "android", "iphone", "ipad"]
    )

    return render(
        request,
        "aichat/chat_conversation.html",
        {
            "selected_ai": selected_ai,
            "ai_models": ai_models,
            "conversation": conversation,
            "messages": messages,
            "is_mobile": is_mobile,
        },
    )


@login_required
@require_http_methods(["DELETE"])
async def delete_conversation(request, conversation_id):
    conversation = await sync_to_async(get_object_or_404)(
        Conversation, id=conversation_id, user=request.user
    )
    await sync_to_async(conversation.soft_delete)()
    return JsonResponse({"success": True})


@login_required
@require_http_methods(["PATCH"])
async def update_conversation_title(request, conversation_id):
    data = json.loads(request.body)
    conversation = await sync_to_async(get_object_or_404)(
        Conversation, id=conversation_id, user=request.user
    )
    conversation.title = data.get("title", "").strip()[:255]
    await sync_to_async(conversation.save)()
    return JsonResponse({"success": True, "title": conversation.title})


@login_required
async def get_ai_response(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        message = request.POST.get("message", "").strip()
        conversation_id = request.POST.get("conversation_id")
        post_id = request.POST.get("post_id")
        image = request.FILES.get("image")

        ai_model = await sync_to_async(AIModel.objects.filter(is_active=True).first)()
        if not ai_model:
            ai_model = await sync_to_async(AIModel.objects.create)(
                name="Gemini Flash 2.0",
                model_id="gemini-1.5-pro",
                model_type="gemini-1.5-pro",
            )

        # Get response
        response_data = await get_gemini_response(
            model=ai_model.model_type, prompt=message, image=image
        )

        # Save conversation and messages
        if conversation_id:
            conversation = await sync_to_async(Conversation.objects.get)(
                id=conversation_id
            )
        else:
            conversation = await sync_to_async(Conversation.objects.create)(
                user=request.user, ai_model=ai_model
            )

        # Save user message
        await sync_to_async(Message.objects.create)(
            conversation=conversation, content=message, is_user=True
        )

        # Save AI response
        await sync_to_async(Message.objects.create)(
            conversation=conversation, content=response_data, is_user=False
        )

        # Update conversation
        if not conversation.title:
            await sync_to_async(conversation.update_title_from_first_message)()

        return JsonResponse(
            {"response": response_data, "conversation_id": str(conversation.id)}
        )

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)


@login_required
def list_ai_models(request):
    models = AIModel.objects.filter(is_active=True).values(
        "id", "name", "description", "model_id", "logo_url"
    )
    return JsonResponse({"models": list(models)})


@login_required
def chat_from_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    selected_ai = AIModel.objects.filter(is_active=True).first()

    # Create a new conversation with post context
    conversation = Conversation.objects.create(
        user=request.user,
        ai_model=selected_ai,
        title=f"Discussion: {post.content[:50]}...",
    )

    return redirect("chat_conversation_view", conversation_id=conversation.id)


@login_required
def feed_posts_json(request):
    posts = Post.objects.filter(is_active=True).order_by("-created_at")[:10]
    data = [
        {
            "id": str(post.id),
            "content": post.content,
            "author": post.author.username,
            "created_at": post.created_at.isoformat(),
        }
        for post in posts
    ]
    return JsonResponse({"posts": data})


@login_required
def save_settings(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_token, created = UserAPIToken.objects.get_or_create(user=request.user)
            user_token.google_gemini_api_key = data.get("google_gemini_api_key")
            user_token.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)


@login_required
async def get_vision_response(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        if "image" not in request.FILES:
            return JsonResponse({"error": "No image provided"}, status=400)

        image_file = request.FILES["image"]
        prompt = request.POST.get("message", "").strip()

        # Use gemini-pro-vision model
        response_data = await get_gemini_response(
            model="gemini-pro-vision", prompt=prompt, image=image_file
        )

        return JsonResponse(
            {
                "response": response_data,
                "finish_reason": "STOP",  # Default finish reason
            }
        )

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
