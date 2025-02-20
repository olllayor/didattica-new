from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from community.models import Post
from .models import Notification
from django.contrib.auth.models import User

@receiver(post_save, sender=Post)
def create_notification(sender, instance, created, **kwargs):
    if created:
        if instance.reply_to and instance.author != instance.reply_to.author:
            if not Notification.objects.filter(
                recipient=instance.reply_to.author,
                sender=instance.author,
                notification_type='comment',
                post=instance
            ).exists():
                Notification.objects.create(
                    recipient=instance.reply_to.author,
                    sender=instance.author,
                    notification_type='comment',
                    post=instance
                )
        elif instance.shared_post and instance.author != instance.shared_post.author:
            if not Notification.objects.filter(
                recipient=instance.shared_post.author,
                sender=instance.author,
                notification_type='repost',
                post=instance.shared_post
            ).exists():
                Notification.objects.create(
                    recipient=instance.shared_post.author,
                    sender=instance.author,
                    notification_type='repost',
                    post=instance.shared_post
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
            Notification.objects.create(
                recipient=post.author,
                sender=user,
                notification_type='like',
                post=post
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
            Notification.objects.create(
                recipient=followed_user,
                sender=follower,
                notification_type='follow'
                # No post field included
            )