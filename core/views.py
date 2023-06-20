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

from core.pagination import GlobalPagination
from core.permissions import IsSuperUserOrDjangoModelPermissions


class DynamicFieldsModelViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperUserOrDjangoModelPermissions]
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
            fields = fields.split(",")
            queryset = queryset.only(*fields)

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
    permission_classes = [IsAuthenticated, IsSuperUserOrDjangoModelPermissions]
    """
    A viewset that provides default `update()`, `partial_update()`, `destroy()` and `list()` actions.
    """
    pass
