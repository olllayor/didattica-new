from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .models import Notification


@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related(
        'sender__profile',
        'post__author'
    ).prefetch_related(
        'post__post_images'
    ).order_by('-created_at')[:50]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        notifications_data = []
        for n in notifications:
            first_image = n.post.post_images.first().image.url if n.post.post_images.exists() else None
            notifications_data.append({
                'id': n.id,
                'sender': n.sender.username,
                'sender_image': n.sender.profile.profile_image.url if n.sender.profile.profile_image else '/static/images/default.webp',
                'type': n.notification_type,
                'post_id': n.post.id,
                'post_image': first_image,
                'post_text': n.post.content if not first_image else None,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat()
            })
        return JsonResponse({'notifications': notifications_data})

    return render(request, 'notifications/list.html', {
        'notifications': notifications
    })

@login_required
def mark_as_read(request, notification_id):
    if request.method == 'POST':
        notification = Notification.objects.filter(
            recipient=request.user,
            id=notification_id
        ).first()
        if notification:
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False}, status=404)
    return JsonResponse({'success': False}, status=405)

@login_required
def mark_all_as_read(request):
    if request.method == 'POST':
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        )
        if unread_notifications.exists():
            unread_notifications.update(is_read=True)
            return JsonResponse({'success': True})
        return JsonResponse({'success': True})  # Success even if no unread notifications
    return JsonResponse({'success': False}, status=405)