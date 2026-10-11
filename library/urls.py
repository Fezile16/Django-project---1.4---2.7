from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.BookListView.as_view(), name='list'),
    path('search/', views.book_search, name='search'),
    path('add/', views.BookCreateView.as_view(), name='add'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.BookUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.BookDeleteView.as_view(), name='delete'),
    path('author/<int:pk>/', views.author_books, name='author-books'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
]