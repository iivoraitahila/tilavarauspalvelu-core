import graphene
from graphene_django.rest_framework.mutation import SerializerMutation
from rest_framework.generics import get_object_or_404

from api.graphql.reservation_units.reservation_unit_serializers import (
    PurposeCreateSerializer,
    PurposeUpdateSerializer,
)
from api.graphql.reservation_units.reservation_unit_types import PurposeType
from reservation_units.models import Purpose


class PurposeCreateMutation(SerializerMutation):
    purpose = graphene.Field(PurposeType)

    class Meta:
        model_operations = ["create"]

        serializer_class = PurposeCreateSerializer

    @classmethod
    def perform_mutate(cls, serializer, info):
        purpose = serializer.create(serializer.validated_data)
        return cls(errors=None, purpose=purpose)


class PurposeUpdateMutation(SerializerMutation):
    purpose = graphene.Field(PurposeType)

    class Meta:
        model_operations = ["update"]
        lookup_field = "pk"
        serializer_class = PurposeUpdateSerializer

    @classmethod
    def perform_mutate(cls, serializer, info):

        validated_data = serializer.validated_data
        pk = validated_data.get("pk")
        purpose = serializer.update(get_object_or_404(Purpose, pk=pk), validated_data)
        return cls(errors=None, purpose=purpose)
