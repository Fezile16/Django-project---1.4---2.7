from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from .forms import BookForm, BookSearchForm, ContactForm
from .models import Author, Book


# ---------- Display views (from the last batch) ----------

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
    """Function-based view: all books by one author."""
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
            'Add, edit and delete books',
        ]
        context['total_books'] = Book.objects.count()
        return context


# ---------- 3.8: a search form processed in a function-based view ----------

def book_search(request):
    form = BookSearchForm(request.GET or None)
    books = Book.objects.none()
    searched = False

    if form.is_valid():
        searched = True
        books = Book.objects.select_related('author')
        query = form.cleaned_data.get('query')
        genre = form.cleaned_data.get('genre')
        min_rating = form.cleaned_data.get('min_rating')
        sort_by = form.cleaned_data.get('sort_by')

        if query:
            books = books.filter(
                Q(title__icontains=query) |
                Q(author__first_name__icontains=query) |
                Q(author__last_name__icontains=query)
            )
        if genre:
            books = books.filter(genre=genre)
        if min_rating:
            books = books.filter(rating__gte=min_rating)
        if sort_by:
            books = books.order_by(sort_by)

    return render(request, 'library/book_search.html', {
        'form': form, 'books': books, 'searched': searched,
    })


# ---------- 3.5: generic edit views ----------

class RedirectToDetailMixin:
    """After saving, go to the book's detail page."""
    def get_success_url(self):
        return reverse('library:detail', args=[self.object.pk])


class BookCreateView(LoginRequiredMixin, SuccessMessageMixin, RedirectToDetailMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_message = 'Book "%(title)s" was created!'


class BookUpdateView(LoginRequiredMixin, SuccessMessageMixin, RedirectToDetailMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_message = 'Book "%(title)s" was updated!'


class BookDeleteView(LoginRequiredMixin, DeleteView):
    model = Book
    template_name = 'library/book_confirm_delete.html'
    success_url = reverse_lazy('library:list')

    def form_valid(self, form):
        messages.success(self.request, f'Book "{self.object.title}" was deleted.')
        return super().form_valid(form)


class ContactView(FormView):
    template_name = 'library/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('library:list')

    def form_valid(self, form):
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']
        send_mail(
            subject=f"Library contact form: {form.cleaned_data['subject']}",
            message=f'From: {name} <{email}>\n\n{message}',
            from_email=email,
            recipient_list=['info@example.com'],
            
        )
        messages.success(self.request, 'Your message has been sent!')
        return super().form_valid(form)