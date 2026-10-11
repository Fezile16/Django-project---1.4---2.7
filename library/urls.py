from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.BookListView.as_view(), name='list'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='detail'),
    path('author/<int:pk>/', views.author_books, name='author-books'),
    path('about/', views.AboutView.as_view(), name='about'),
]