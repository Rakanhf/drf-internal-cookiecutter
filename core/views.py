# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from core.pagination import GlobalPagination
from core.permissions import DynamicAccessPermission


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="fields",
            type=OpenApiTypes.STR,
            description="Comma-separated list of fields to include in the response",
            required=False,
        )
    ]
)
class DynamicFieldsModelViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, DynamicAccessPermission]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    pagination_class = GlobalPagination

    """
    A ModelViewSet that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        fields = self.request.query_params.get("fields")

        if fields:
            requested_fields = set(fields.split(","))
            valid_fields = {
                field.name
                for field in self.serializer_class.Meta.model._meta.get_fields()
            }

            # Only apply 'only' if there are valid fields requested
            if requested_fields & valid_fields:
                queryset = queryset.only(*requested_fields & valid_fields)

        return queryset

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        fields = self.request.query_params.get("fields")
        if fields:
            context.update({"fields": fields.split(",")})
        return context


class ListUpdateViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, DynamicAccessPermission]
    """
    A viewset that provides default `update()`, `partial_update()`, `destroy()` and `list()` actions.
    """
    pass
