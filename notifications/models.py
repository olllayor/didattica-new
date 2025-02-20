from django.db import models
from django.contrib.auth.models import User
from community.models import Post

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('repost', 'Repost'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        # ('mention', 'Mention'),
        # ('reply', 'Reply'),
        
        
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.username} {self.notification_type}d {self.post.id} for {self.recipient.username}"
    
    @staticmethod
    def get_unread_count(user):
        return Notification.objects.filter(recipient=user, is_read=False).count()