from django.shortcuts import redirect
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from django.db.models import Q
from django.http import JsonResponse
from django.http import HttpResponse

from .models import *
from .forms import *

# Create your views here.

class GenreYear():
    """Жанры и годавыхода фильмов"""
    def get_genres(self):
        return Genre.objects.all()
    
    def get_years(self):
        return Movie.objects.filter(draft=False).values("year")



class MoviesView(GenreYear,ListView):
    """Список фильмов"""
    model = Movie
    queryset = Movie.objects.filter(draft=False).order_by('id')
    paginate_by = 1
#    template_name = "movies/movies.html" #if do not use this it will add list
    
    def get_context_data(self, *args, **kwargs,):
        context = super().get_context_data(*args, **kwargs)
        context["categories"] = Category.objects.all()
        return context

    




class MovieDetailView(GenreYear,DetailView):
    """Полное описание фильма"""
    model = Movie      #template_name не нужен так как сам находит муви А Детаил добавляется автоматически
    queryset = Movie.objects.filter(draft=False)
    slug_field = "url"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["star_form"] = RatingForm()
        context["form"] = ReviewForm()
        return context


class AddReview(View):
    """Отзывы"""
    def post(self, request, pk):
        form = ReviewForm(request.POST)
        movie = Movie.objects.get(id=pk)
        if form.is_valid():
            form = form.save(commit=False)
            if request.POST.get("parent", None):
                form.parent_id = int(request.POST.get("parent"))
            form.movie = movie
            form.save()
        return redirect(movie.get_absolute_url()) 

class ActorView(GenreYear, DetailView):
    """Вывод информации об актере"""
    model = Actor
    template_name = 'movies/actor.html'
    slug_field = "name"

class FilterMoviesView(GenreYear, ListView):
    """Фильтр фильмов"""
    paginate_by: int = 1
    def get_queryset(self):
        queryset = Movie.objects.filter(
            Q(year__in=self.request.GET.getlist("year")) |
            Q(genres__in=self.request.GET.getlist("genre"))
            ).distinct()
        return queryset
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["year"] =''.join([f"year={x}&" for x in self.request.GET.getlist("year")])
        context["genre"] =''.join([f"genre={x}&" for x in self.request.GET.getlist("genre")])
        return context
    
class JsonFilterMoviesView(ListView):
    """Фильтр фильмов в json"""
    def get_queryset(self):
        queryset = Movie.objects.filter(
            Q(year__in=self.request.GET.getlist("year")) |
            Q(genres__in=self.request.GET.getlist("genre"))
        ).distinct().values("title", "tagline", "url", "poster")
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = list(self.get_queryset())
        return JsonResponse({"movies": queryset}, safe=False)


class AddStarRating(View):
    """Добавление рейтинга фильму"""
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                ip=self.get_client_ip(request),
                movie_id=int(request.POST.get("movie")),
                defaults={'star_id': int(request.POST.get("star"))}
            )
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)

class Search(ListView):
    """Поиск фильмов"""
    paginate_by: int = 3

    def get_queryset(self):
        q = self.request.GET.get('q')
        a = "".join(q[0].upper()) + q[1:]
        return Movie.objects.filter(title__icontains=a)

    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["q"] = f'q={self.request.GET.get("q")}&'
        return context
    
    