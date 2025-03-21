import graphene
from graphene import Field, relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphene_permissions.mixins import AuthFilter
from graphene_permissions.permissions import AllowAuthenticated
from rest_framework.generics import get_object_or_404

from api.graphql.reservation_units.reservation_unit_mutations import (
    PurposeCreateMutation,
    PurposeUpdateMutation,
)
from api.graphql.reservation_units.reservation_unit_types import ReservationUnitType
from api.graphql.reservations.reservation_types import ReservationType
from api.graphql.resources.resource_types import ResourceType
from api.graphql.spaces.space_mutations import SpaceCreateMutation, SpaceUpdateMutation
from api.graphql.spaces.space_types import SpaceType
from reservation_units.models import ReservationUnit
from reservations.forms import ReservationForm
from resources.models import Resource


class ReservationMutation(DjangoModelFormMutation):
    reservation = graphene.Field(ReservationType)

    class Meta:
        form_class = ReservationForm


class AllowAuthenticatedFilter(AuthFilter):
    permission_classes = (AllowAuthenticated,)


class Query(graphene.ObjectType):
    reservation_units = DjangoFilterConnectionField(ReservationUnitType)
    reservation_unit = relay.Node.Field(ReservationUnitType)
    reservation_unit_by_pk = Field(ReservationUnitType, pk=graphene.Int())

    resources = DjangoFilterConnectionField(ResourceType)
    resource = relay.Node.Field(ResourceType)
    resource_by_pk = Field(ResourceType, pk=graphene.Int())

    spaces = DjangoFilterConnectionField(SpaceType)
    space = relay.Node.Field(SpaceType)
    space_by_pk = Field(SpaceType, pk=graphene.Int())

    def resolve_reservation_unit_by_pk(parent, info, **kwargs):
        pk = kwargs.get("pk")
        return get_object_or_404(ReservationUnit, pk=pk)

    def resolve_resource_by_pk(parent, info, **kwargs):
        pk = kwargs.get("pk")
        return get_object_or_404(Resource, pk=pk)


class Mutation(graphene.ObjectType):
    create_reservation = ReservationMutation.Field()

    create_purpose = PurposeCreateMutation.Field()
    update_purpose = PurposeUpdateMutation.Field()

    create_space = SpaceCreateMutation.Field()
    update_space = SpaceUpdateMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
