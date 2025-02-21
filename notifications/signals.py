from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from community.models import Post
from .models import Notification
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

@receiver(post_save, sender=Post)
def create_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        if instance.reply_to and instance.author != instance.reply_to.author:
            if not Notification.objects.filter(
                recipient=instance.reply_to.author,
                sender=instance.author,
                notification_type='comment',
                post=instance
            ).exists():
                notification = Notification.objects.create(
                    recipient=instance.reply_to.author,
                    sender=instance.author,
                    notification_type='comment',
                    post=instance
                )
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{instance.reply_to.author.id}',
                    {
                        'type': 'send_notification',
                        'notification': {
                            'id': notification.id,
                            'sender': notification.sender.username,
                            'type': notification.notification_type,
                            'post_id': notification.post.id,
                            'is_read': notification.is_read,
                            'created_at': notification.created_at.isoformat()
                        }
                    }
                )
        elif instance.shared_post and instance.author != instance.shared_post.author:
            if not Notification.objects.filter(
                recipient=instance.shared_post.author,
                sender=instance.author,
                notification_type='repost',
                post=instance.shared_post
            ).exists():
                notification = Notification.objects.create(
                    recipient=instance.shared_post.author,
                    sender=instance.author,
                    notification_type='repost',
                    post=instance.shared_post
                )
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{instance.shared_post.author.id}',
                    {
                        'type': 'send_notification',
                        'notification': {
                            'id': notification.id,
                            'sender': notification.sender.username,
                            'type': notification.notification_type,
                            'post_id': notification.post.id,
                            'is_read': notification.is_read,
                            'created_at': notification.created_at.isoformat()
                        }
                    }
                )

like_created = Signal()

@receiver(like_created)
def create_like_notification(sender, post, user, **kwargs):
    if user != post.author:
        if not Notification.objects.filter(
            recipient=post.author,
            sender=user,
            notification_type='like',
            post=post
        ).exists():
            notification = Notification.objects.create(
                recipient=post.author,
                sender=user,
                notification_type='like',
                post=post
            )
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notifications_{post.author.id}',
                {
                    'type': 'send_notification',
                    'notification': {
                        'id': notification.id,
                        'sender': notification.sender.username,
                        'type': notification.notification_type,
                        'post_id': notification.post.id,
                        'is_read': notification.is_read,
                        'created_at': notification.created_at.isoformat()
                    }
                }
            )

follow_created = Signal()

@receiver(follow_created)
def create_follow_notification(sender, follower, followed_user, **kwargs):
    if follower != followed_user:
        if not Notification.objects.filter(
            recipient=followed_user,
            sender=follower,
            notification_type='follow'
        ).exists():
            notification = Notification.objects.create(
                recipient=followed_user,
                sender=follower,
                notification_type='follow'
            )
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notifications_{followed_user.id}',
                {
                    'type': 'send_notification',
                    'notification': {
                        'id': notification.id,
                        'sender': notification.sender.username,
                        'type': notification.notification_type,
                        'post_id': None,
                        'is_read': notification.is_read,
                        'created_at': notification.created_at.isoformat()
                    }
                }
            )