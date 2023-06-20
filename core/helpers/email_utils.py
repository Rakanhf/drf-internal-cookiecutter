# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


import os
from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class EmailHelper:
    def __init__(self, subject, template_name, context=None, bcc=None):
        self.subject = subject
        self.template_name = template_name
        self.context = context or {}
        self.bcc = bcc or []

    def send_email(self, to_email):
        html_content = render_to_string(self.template_name, self.context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=self.subject,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email],
            bcc=self.bcc,
        )

        # Attach all the inline images
        image_files = ["logo.png"]
        for image_file in image_files:
            image_path = os.path.join("core/templates/emails/images", image_file)
            with open(image_path, "rb") as img:
                image = MIMEImage(img.read())
                img.close()
            image_name = os.path.splitext(image_file)[0]
            image.add_header("Content-ID", f"<{image_name}>")
            email.attach(image)

        # Attach the HTML content
        email.attach_alternative(html_content, "text/html")

        # Send the email
        email.send()
