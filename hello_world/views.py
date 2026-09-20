from django.http import HttpResponse

def hello_world(request):
    html = """
    <html>
    <head>
        <title>Hello,World!</title>
    </head>
    <body>
        <h1 style="color: blue;">Hello,World!</h1>
        <p>Welcome to Django!</p>
    </body>
    </html>
    """
    return HttpResponse(html)