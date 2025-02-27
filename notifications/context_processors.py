from .models import Notification

def notification_count(request):
    if request.user.is_authenticated:
        return {'notification_unread_count': Notification.get_unread_count(request.user)}
    return {'notification_unread_count': 0}