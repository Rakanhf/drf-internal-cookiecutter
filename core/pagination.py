# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination


class GlobalPagination(PageNumberPagination):
    """
    A simple page number based style that supports page numbers as
    query parameters. For example:

    https://api.example.com/users/?page=4
    https:/api.example.com/users/?page=4&page_size=100
    """

    # Setting the default page size to 10
    page_size = 10
    # Setting the maximum page size to 100
    max_page_size = 100

    # Overriding the get_page_size method to return the paginated response in the desired format
    def get_page_size(self, request):
        page_size = request.query_params.get("page_size", self.page_size)
        try:
            page_size = int(page_size)
        except ValueError:
            raise ValidationError(
                {"detail": "Invalid page size value. It must be an integer."}
            )
        if page_size > self.max_page_size:
            raise ValidationError(
                {"detail": f"Maximum page size is {self.max_page_size}"}
            )
        return page_size
