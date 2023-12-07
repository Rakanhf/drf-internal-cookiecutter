# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from drf_spectacular.openapi import AutoSchema
import re


class CustomAutoSchema(AutoSchema):
    """
    Custom schema class for DRF spectacular that provides enhanced features
    like natural language operation IDs, custom tagging, and filter field enumeration.
    """

    def get_tags(self):
        """
        Override to provide custom tags for the API endpoints. Tags are determined
        based on the view's name or URL, with a fallback to the default logic.
        """
        view_name = self._view.__class__.__name__.lower()
        url_name = getattr(self._view, "url_name", "").lower()

        if "password" in view_name or "password" in url_name:
            return ["Reset Password"]

        return [
            getattr(
                self._view,
                "drf_tag",
                self._view.__class__.__name__.replace("ViewSet", ""),
            )
        ]

    def get_description(self):
        """
        Override to extract and provide a custom description for the API endpoints.
        The description is extracted from the docstring of the view.
        """
        doc = self._view.__doc__
        if doc:
            description_lines = [
                line.strip() for line in doc.split("\n") if line.strip().startswith("*")
            ]
            return " ".join(description_lines).strip("*") if description_lines else None
        return f"{self._view.__class__.__name__} operations"

    def get_filter_fields(self):
        """
        Generates a list of available filter, search, and ordering fields for the view.
        """
        if hasattr(self._view, "filter_backends"):
            filter_backends = self._view.filter_backends
            fields = []
            for backend in filter_backends:
                if hasattr(backend, "get_filterset_class"):
                    filterset_class = backend.get_filterset_class(
                        self._view, self._view
                    )
                    if filterset_class:
                        fields.extend(filterset_class().get_fields())
                elif hasattr(backend, "search_fields"):
                    fields.extend(backend.search_fields or [])
                elif hasattr(backend, "ordering_fields"):
                    fields.extend(backend.ordering_fields or [])
            return fields
        return []

    def get_operation_id(self):
        """
        Generates a more readable, natural language format for operation IDs.
        """
        operation_id = super().get_operation_id()
        try:
            return self._reformat_operation_id(operation_id)
        except Exception as e:
            print(f"Error in reformating operation ID: {e}")
            return operation_id

    def _reformat_operation_id(self, operation_id):
        """
        Helper method to reformat the operation ID into a more readable format.
        """
        readable_operation_id = operation_id.replace("_", " ").title()
        list_pattern = re.compile(r"(.*)List$")
        create_pattern = re.compile(r"(.*)Create$")
        if list_pattern.match(readable_operation_id):
            return "List " + list_pattern.sub(r"\1", readable_operation_id)
        elif create_pattern.match(readable_operation_id):
            return "Create " + create_pattern.sub(r"\1", readable_operation_id)
        return readable_operation_id

    def get_operation(self, path, path_regex, path_prefix, method, registry):
        """
        Override to add custom fields to the schema operation.
        """
        operation = super().get_operation(
            path, path_regex, path_prefix, method, registry
        )
        if operation is not None:
            operation["x-custom-filter-fields"] = self.get_filter_fields()
        return operation


def tag_view(view_class, tag):
    """
    Helper function to tag a DRF view with a specific tag for API documentation.
    """

    class TaggedView(view_class):
        drf_tag = tag

    return TaggedView
