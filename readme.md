
# Django Rest Framework Cookiecutter

_A Production ready project that aims to kickstart building API based internal tools for business._

# <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green" /> 

[![Build Status](https://img.shields.io/github/actions/workflow/status/cookiecutter/cookiecutter-django/ci.yml?branch=master)](https://github.com/cookiecutter/cookiecutter-django/actions/workflows/ci.yml?query=branch%3Amaster) [![Documentation Status](https://readthedocs.org/projects/cookiecutter-django/badge/?version=latest)](https://cookiecutter-django.readthedocs.io/en/latest/?badge=latest) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- For Django 4.1

- Works with Python 3.11

- [python-decouple](https://pypi.org/project/python-decouple/) based settings
- Folder based settings structure
- Secure by default.

- Optimized development and production settings

- Authentication via [djangorestframework-simplejwt](https://github.com/jazzband/djangorestframework-simplejwt)

- Comes with custom user model ready to go

- Media storage using nginx

- 2FA Built in using [django-otp](https://github.com/django-otp/django-otp)

- Custom login middleware to login using email or phone number

- Logging built in using [django-auditlog](https://github.com/jazzband/django-auditlog)

- Cors headers built in using [django-cors-headers](https://github.com/adamchainz/django-cors-headers)

- Minimal Device detection management using a custom model via [django-user_agents](https://github.com/selwin/django-user_agents)

- Standardized API error response format using [drf-standardized-errors](https://github.com/ghazi-git/drf-standardized-errors)

- Custom SMS, Email templates ready to use
-  Twilio integration 
- Custom email handler
- Throttling built in

- Password reset endpoints built in

- Ready to use Account management endpoints (Users, Groups, Permissions, etc.)

- Ready to use Auth endpoints (Login, Logout, 2FA, Reset Password etc.)

- 43 endpoints ready to use

- Optimized ModelViewSet for all endpoints that includes
	- Authentication
	- Permissions
	- Filters
	- Pagination
	- Custom queryset for ORM optimized `?fields` parameter
- Custom pagination
- OpenAPI documentation ready using [drf-spectacular.](https://github.com/tfranzel/drf-spectacular)
- Email login notifications for unrecognized devices 

## Requirements
Python 3.7 to 3.11 supported.
Django 3.2 to 4.2 supported.

## 2FA Overview

_2FA is enabled by default for all options 'SMS', 'EMAIL', 'TOTP' devices ._

### Workflow
![2FA Flow](https://res.cloudinary.com/dmledf14h/image/upload/c_pad,b_auto:predominant,fl_preserve_transparency/v1685643856/2FA_i6xoad.jpg?_s=public-apps)

## Usage
First, clone drf-cookiecutter
```bash
git clone https://github.com/Rakanhf/drf-cookiecutter.git
```
Optional : Rename project from `mainbrain` to your desired name

Secondly : 
   ```bash
pip install -r requirements-dev.txt
```

Thirdly :
- Generate a secret key follow [this tutorial](https://codinggear.blog/django-generate-secret-key/)
- Rename `.env.sample` to `.env` and fill in the variables

Finally :
   ```bash
python manage.py runserver
```

Amazing! now just run the server and it's all done :)

## Configuration
### `OTP_DEVICE_CLASSES: dict`
Adding the desired 2FA methods 
Example:
```python
OTP_DEVICE_CLASSES = {
	"totp": "otp_totp.TOTPDevice",
	"email": "authentication.CustomEmailDevice",
}
```
### `RESET_PASSWORD_URL: str`
Add the dashboard rout URL 
Example:
```python
RESET_PASSWORD_URL = "http://localhost:3000/auth/reset-password/"
# Link output :
# http://localhost:3000/auth/reset-password/{Token-Here}
```
### `OTP_SMS_BODY_TEMPLATE: str, OTP_EMAIL_BODY_TEMPLATE: str`
This is the location of the body template for the sms, email
Example:
```python
OTP_SMS_BODY_TEMPLATE = os.path.join(BASE_DIR, "core/templates/emails/auth/sms_otp.html")
```

## API Docs 
_I have included the openapi schema so you can use it with your personal favorite API docs framework ._
* Swagger UI
```bash
http://127.0.0.1:8000/docs/
```
* Redoc UI
```bash
http://127.0.0.1:8000/docs/redoc/
```

## Testing
_This project uses [coverage](https://github.com/nedbat/coveragepy) to measure the code coverage of the tests._
```bash
coverage run --omit='*/.venv/*' manage.py test
```

## Notes
- There is no built in registration endpoint since the aim of this project is accelerate building of internal tools and in many cases the users get created by the superuser instead.

