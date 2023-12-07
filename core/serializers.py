# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#

from rest_framework import serializers


class DynamicFieldsSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(DynamicFieldsSerializer, self).__init__(*args, **kwargs)

        requested_fields = self.get_requested_fields(kwargs.get("context", {}))

        if requested_fields is not None:
            valid_fields = set(self.fields.keys())
            # Keep only valid fields from requested fields
            valid_requested_fields = set(
                field for field in requested_fields if field in valid_fields
            )

            # If no valid fields are requested, do not alter the fields
            if valid_requested_fields:
                for field_name in valid_fields - valid_requested_fields:
                    self.fields.pop(field_name)

    def get_requested_fields(self, context):
        """
        Get the list of requested fields from the request's "fields" query param
        """
        request = context.get("request")
        fields_query_param = request.GET.get("fields", "") if request else None
        return fields_query_param.split(",") if fields_query_param else None
