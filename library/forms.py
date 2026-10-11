from django import forms
from django.utils import timezone

from .models import Book


class BookForm(forms.ModelForm):
    """ModelForm: Django builds the form fields from the Book model."""

    # Override so hyphens are allowed while typing (the model only stores digits)
    isbn = forms.CharField(max_length=17, help_text='10 or 13 digits. Hyphens are allowed.')

    class Meta:
        model = Book
        fields = [
            'title', 'subtitle', 'isbn', 'author', 'publisher',
            'publication_date', 'genre', 'genres', 'pages',
            'summary', 'is_available', 'rating',
        ]
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'summary': forms.Textarea(attrs={'rows': 5}),
            'genres': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'title': 'Book Title',
            'publication_date': 'Date Published',
            'genre': 'Main Genre',
            'genres': 'Extra Genre Tags',
        }
        help_texts = {'rating': 'Rate the book from 1 to 5.'}

    # Field-level validation: clean_<fieldname>()
    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn', '')
        cleaned = ''.join(c for c in isbn if c.isdigit())
        if len(cleaned) not in (10, 13):
            raise forms.ValidationError('ISBN must be 10 or 13 digits.')

        queryset = Book.objects.filter(isbn=cleaned)
        if self.instance.pk:  # when editing, ignore the book itself
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError('A book with this ISBN already exists.')
        return cleaned

    def clean_publication_date(self):
        date = self.cleaned_data['publication_date']
        if date > timezone.now().date():
            raise forms.ValidationError('Publication date cannot be in the future.')
        return date

    # Form-level validation: compares several fields
    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        subtitle = cleaned_data.get('subtitle')
        if title and subtitle and title.lower() == subtitle.lower():
            raise forms.ValidationError('Subtitle cannot be identical to the title.')
        return cleaned_data


class BookSearchForm(forms.Form):
    """A plain (non-model) form used for searching."""
    query = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Title or author...'}),
    )
    genre = forms.ChoiceField(
        choices=[('', 'All genres')] + Book.GENRE_CHOICES,
        required=False,
    )
    min_rating = forms.IntegerField(required=False, min_value=1, max_value=5, label='Minimum rating')
    sort_by = forms.ChoiceField(
        choices=[
            ('title', 'Title (A-Z)'), ('-title', 'Title (Z-A)'),
            ('-rating', 'Highest rated'), ('-publication_date', 'Newest'),
        ],
        required=False,
    )


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Your name')
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))