import re

from django import template

from ..models import Book

register = template.Library()


# --- Custom filters ---

@register.filter(name='stars')
def stars(rating, max_stars=5):
    """Turn 4 into ★★★★☆"""
    if not rating:
        return ''
    full = int(rating)
    return '★' * full + '☆' * (int(max_stars) - full)


@register.filter(name='reading_time')
def reading_time(text, words_per_minute=200):
    """Estimate reading time from the word count."""
    if not text:
        return '0 min read'
    word_count = len(re.findall(r'\w+', text))
    minutes = max(1, int(word_count / int(words_per_minute)))
    return f'{minutes} min read'


# --- Simple tag (used with "as") ---

@register.simple_tag
def get_random_books(count=3):
    return Book.objects.order_by('?')[:count]


# --- Inclusion tag: renders a reusable template fragment ---

@register.inclusion_tag('library/includes/book_card.html')
def book_card(book):
    return {'book': book}