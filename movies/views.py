from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Report, REPORT_THRESHOLD
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})
def show(request, id):
    movie = Movie.objects.get(id=id)
    template_data = {}
    reviews = list(Review.objects.filter(movie=movie, is_hidden=False))
    if request.user.is_authenticated:
        reported_ids = set(Report.objects.filter(
            user=request.user, review__in=reviews
        ).values_list('review_id', flat=True))
        for review in reviews:
            review.reported_by_me = review.id in reported_ids
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['report_reasons'] = Report.REASON_CHOICES
    return render(request, 'movies/show.html',
                  {'template_data': template_data})
@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)
@login_required
def report_review(request, id, review_id):
    if request.method != 'POST':
        return redirect('movies.show', id=id)
    review = get_object_or_404(Review, id=review_id, movie_id=id)
    if review.user == request.user:
        messages.error(request,
            'You cannot report your own review.')
        return redirect('movies.show', id=id)
    reason = request.POST.get('reason', 'other')
    if reason not in dict(Report.REASON_CHOICES):
        reason = 'other'
    report, created = Report.objects.get_or_create(
        review=review, user=request.user,
        defaults={'reason': reason})
    if not created:
        messages.info(request,
            'You have already reported this review.')
        return redirect('movies.show', id=id)
    if review.reports.count() >= REPORT_THRESHOLD:
        review.is_hidden = True
        review.save()
        messages.success(request,
            'Thanks. This review has been removed from the page.')
    else:
        messages.success(request,
            'Thanks. Your report has been submitted for review.')
    return redirect('movies.show', id=id)
