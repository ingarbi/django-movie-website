from django.core.mail import send_mail

def send(user_email):
    send_mail(
        'You have just signed UP for mailing ',
        "We are going to SPAM you",
        'ingarbi006@gmail.com',
        [user_email],
        fail_silently=False
    )