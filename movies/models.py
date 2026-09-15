from django.db import models
from django.contrib.auth.models import User

# Number of distinct user reports required before a review is
# automatically hidden from the movie page. Change this single value
# to make moderation stricter (1 = removed on first report) or looser.
REPORT_THRESHOLD = 3

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    def __str__(self):
        return str(self.id) + ' - ' + self.name
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie,
        on_delete=models.CASCADE)
    user = models.ForeignKey(User,
        on_delete=models.CASCADE)
    is_hidden = models.BooleanField(default=False)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
class Report(models.Model):
    REASON_CHOICES = [
        ('spam', 'Spam or advertising'),
        ('offensive', 'Offensive or abusive language'),
        ('irrelevant', 'Irrelevant to this movie'),
        ('spoiler', 'Contains spoilers'),
        ('other', 'Other'),
    ]
    id = models.AutoField(primary_key=True)
    review = models.ForeignKey(Review,
        on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User,
        on_delete=models.CASCADE)
    reason = models.CharField(max_length=20,
        choices=REASON_CHOICES, default='other')
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['review', 'user'],
                name='unique_report_per_user_per_review')
        ]
    def __str__(self):
        return str(self.id) + ' - report on review ' + str(self.review_id)
