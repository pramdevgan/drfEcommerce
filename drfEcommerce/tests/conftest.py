import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient
from .factories import CategoryFactory, \
    ProductFactory, ProductLineFactory, \
    ProductImageFactory, ProductTypeFactory, \
    AttributeFactory, AttributeValueFactory, \
    ProductLineAttributeValueFactory, \
    OrderFactory, UserFactory

register(CategoryFactory)
register(ProductFactory)
register(ProductLineFactory)
register(ProductImageFactory)
register(ProductTypeFactory)
register(AttributeValueFactory)
register(AttributeFactory)
register(ProductLineAttributeValueFactory)
register(OrderFactory)
register(UserFactory)


@pytest.fixture
def api_client():
    return APIClient


@pytest.fixture
def order(user, product):
    return OrderFactory(user=user, product=product)
