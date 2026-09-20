from django.contrib import admin
from .models import Author, Publisher, Book, Genre


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'publication_date', 'is_available', 'rating')
    list_filter = ('genre', 'is_available')
    search_fields = ('title', 'author__first_name', 'author__last_name', 'isbn')


admin.site.register(Author)
admin.site.register(Publisher)
admin.site.register(Genre)