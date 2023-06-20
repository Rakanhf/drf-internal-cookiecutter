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
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(requested_fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def get_requested_fields(self, context):
        """
        Get the list of requested fields from the request's "fields" query param
        """
        request = context.get("request")
        fields_query_param = request.GET.get("fields", "") if request else None
        return fields_query_param.split(",") if fields_query_param else None
