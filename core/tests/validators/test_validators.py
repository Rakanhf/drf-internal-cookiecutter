# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from core.validators import validate_file_extension, validate_image_file_extension


class ValidatorsTest(TestCase):
    def test_validate_file_extension_valid(self):
        valid_file = SimpleUploadedFile(
            "document.pdf", b"file_content", content_type="application/pdf"
        )
        # Should not raise a ValidationError
        validate_file_extension(valid_file)

    def test_validate_file_extension_invalid(self):
        invalid_file = SimpleUploadedFile(
            "document.txt", b"file_content", content_type="text/plain"
        )
        with self.assertRaises(ValidationError):
            validate_file_extension(invalid_file)

    def test_validate_image_file_extension_valid(self):
        valid_image = SimpleUploadedFile(
            "image.jpg", b"file_content", content_type="image/jpeg"
        )
        # Should not raise a ValidationError
        validate_image_file_extension(valid_image)

    def test_validate_image_file_extension_invalid(self):
        invalid_image = SimpleUploadedFile(
            "image.gif", b"file_content", content_type="image/gif"
        )
        with self.assertRaises(ValidationError):
            validate_image_file_extension(invalid_image)
