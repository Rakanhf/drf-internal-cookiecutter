# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#

import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()
faker = Faker()


class Command(BaseCommand):
    help = "Creates initial permission groups, users, and profiles."

    def handle(self, *args, **kwargs):
        try:
            self.create_groups()
            self.create_users()
            print("Groups and users have been imported.")
        except IntegrityError:
            print("Groups and users have been already imported.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def create_groups(self):
        # Permissions for 'account manager' and 'support' groups
        account_manager_perms = [
            "add_user",
            "change_user",
            "view_user",
            "add_profile",
            "change_profile",
            "view_profile",
            "add_logentry",
            "change_logentry",
            "view_logentry",
            "add_group",
            "change_group",
            "view_group",
        ]
        support_perms = [
            "add_user",
            "change_user",
            "view_user",
            "add_profile",
            "change_profile",
            "view_profile",
            "add_logentry",
            "change_logentry",
            "view_logentry",
        ]

        # Create groups and assign permissions
        account_manager_group, _ = Group.objects.get_or_create(name="account manager")
        account_manager_group.permissions.set(
            Permission.objects.filter(codename__in=account_manager_perms)
        )

        support_group, _ = Group.objects.get_or_create(name="support")
        support_group.permissions.set(
            Permission.objects.filter(codename__in=support_perms)
        )

        # Admin group with all permissions
        admin_group, _ = Group.objects.get_or_create(name="admin access")
        admin_group.permissions.set(Permission.objects.all())

    def create_users(self):
        # Known users
        known_users = [
            {
                "email": "rakan@test.com",
                "phone_number": "+90544447680",
                "group": "admin access",
                "first_name": "Rakan",
                "last_name": "Farhouda",
            },
            {
                "email": "demo.user@test.com",
                "phone_number": "+905523669081",
                "group": "admin access",
                "first_name": "demo",
                "last_name": "user",
            },
        ]
        for user_data in known_users:
            user = User.objects.create_user(
                email=user_data["email"],
                password="Test_123",
                phone_number=user_data["phone_number"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
            )
            user.groups.add(Group.objects.get(name=user_data["group"]))
            self.edit_profile(user)

        # Random users
        other_groups = ["account manager", "support"]
        for i in range(8):
            email = f"randomuser{i}@Test.com"
            phone_number = "+905" + "".join(
                [str(random.randint(0, 9)) for _ in range(7)]
            )
            group = random.choice(other_groups)
            user = User.objects.create_user(
                email=email,
                password="Test_123",
                phone_number=phone_number,
                first_name=faker.first_name(),
                last_name=faker.last_name(),
            )
            user.groups.add(Group.objects.get(name=group))
            self.edit_profile(user)

    def edit_profile(self, user):
        profile = user.profile
        profile.bio = faker.text(
            max_nb_chars=200, ext_word_list=None
        )  # Random text in MD format
        profile.country = faker.country()
        profile.city = faker.city()
        profile.state = faker.state()
        profile.address = faker.address()
        profile.postal_code = faker.postalcode()
        profile.occupation = faker.job()
        profile.save()
