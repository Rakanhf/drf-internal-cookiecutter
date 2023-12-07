# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@test.com", password="testpass"
        )
        self.profile = Profile.objects.get(user=self.user)

    def test_auto_generated(self):
        self.assertEqual(self.profile.user, self.user)

    def test_edit(self):
        self.profile.first_name = "Test"
        self.profile.last_name = "User"
        self.profile.save()
        self.assertEqual(self.profile.first_name, "Test")
        self.assertEqual(self.profile.last_name, "User")
