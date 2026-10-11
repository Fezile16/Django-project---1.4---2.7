from django.shortcuts import render

# Create your views here.

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView

from .models import Author, Book


class BookListView(ListView):
    """Class-based list view with search, genre filter and pagination."""
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset().select_related('author', 'publisher')
        search_query = self.request.GET.get('q')
        genre = self.request.GET.get('genre')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__first_name__icontains=search_query) |
                Q(author__last_name__icontains=search_query)
            )
        if genre:
            queryset = queryset.filter(genre=genre)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop('page', None)
        context['query_string'] = params.urlencode()
        context['search_query'] = self.request.GET.get('q', '')
        context['genre'] = self.request.GET.get('genre', '')
        context['genre_choices'] = Book.GENRE_CHOICES
        context['total_books'] = Book.objects.count()
        return context


class BookDetailView(DetailView):
    """Class-based detail view for one book."""
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'

    def get_queryset(self):
        return super().get_queryset().select_related('author', 'publisher').prefetch_related('genres')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object
        context['similar_books'] = (
            Book.objects.filter(genre=book.genre).exclude(pk=book.pk).order_by('-rating')[:5]
        )
        context['author_books'] = (
            Book.objects.filter(author=book.author).exclude(pk=book.pk)[:5]
        )
        return context


def author_books(request, pk):
    """Function-based view: all books by one author (pk comes from the URL)."""
    author = get_object_or_404(Author, pk=pk)
    books = author.books.all()
    return render(request, 'library/author_books.html', {'author': author, 'books': books})


class AboutView(TemplateView):
    template_name = 'library/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['library_name'] = 'My Library'
        context['features'] = [
            'Browse the whole collection',
            'Search by title or author',
            'Filter books by genre',
        ]
        context['total_books'] = Book.objects.count()
        return context