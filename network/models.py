from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    content = models.CharField(max_length=140)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    date = models.DateTimeField(auto_now_add=True)

    @property
    def likes(self):
        return Like.objects.filter(post=self).count()

    def __str__(self):
        return f"Post {self.id} made by {self.user} on {self.date.strftime('%d %b %Y %H %M %S')}"
    
class Follow(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="following")
    follower = models.ForeignKey(User,on_delete=models.CASCADE, related_name="followed")

    def __str__(self):
        return f"{self.user} is following {self.follower}"
    
class Like(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="liker")
    post = models.ForeignKey(Post,on_delete=models.CASCADE, related_name="liked_post")

    def __str__(self):
        return f"{self.user} liked {self.post}"