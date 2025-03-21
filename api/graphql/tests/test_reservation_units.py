import json

import snapshottest
from assertpy import assert_that
from graphene_django.utils import GraphQLTestCase
from rest_framework.test import APIClient

from reservation_units.tests.factories import (
    ReservationUnitFactory,
    ReservationUnitTypeFactory,
)


class ReservationUnitTestCase(GraphQLTestCase, snapshottest.TestCase):
    @classmethod
    def setUpTestData(cls):
        type = ReservationUnitTypeFactory(name="Test type")
        cls.reservation_unit = ReservationUnitFactory(
            name="Test name", reservation_unit_type=type
        )

        cls.api_client = APIClient()

    def test_getting_reservation_units(self):
        response = self.query(
            """
            query {
                reservationUnits {
                    edges {
                        node {
                            name
                            description
                            spaces {
                              name
                            }
                            resources {
                              name
                            }
                            services {
                              name
                            }
                            requireIntroduction
                            purposes {
                              name
                            }
                            images {
                              imageUrl
                              mediumUrl
                              smallUrl
                            }
                            location {
                              longitude
                              latitude
                            }
                            maxPersons
                            reservationUnitType {
                              name
                            }
                            termsOfUse
                            equipment {
                              name
                            }
                            contactInformation
                          }
                        }
                    }
                }
            """
        )

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

    def test_should_be_able_to_find_by_pk(self):
        query = (
            f"{{\n"
            f"reservationUnitByPk(pk: {self.reservation_unit.id}) {{\n"
            f"id name pk\n"
            f"}}"
            f"}}"
        )
        response = self.query(query)

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("reservationUnitByPk").get("pk")
        ).is_equal_to(self.reservation_unit.id)

    def test_should_error_when_not_found_by_pk(self):
        query = (
            f"{{\n"
            f"reservationUnitByPk(pk: {self.reservation_unit.id + 666}) {{\n"
            f"id\n"
            f"}}"
            f"}}"
        )
        response = self.query(query)

        content = json.loads(response.content)
        errors = content.get("errors")
        assert_that(len(errors)).is_equal_to(1)
        assert_that(errors[0].get("message")).is_equal_to(
            "No ReservationUnit matches the given query."
        )
