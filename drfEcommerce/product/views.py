from django.db import connection
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import SqlLexer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from sqlparse import format
from django.views.decorators.csrf import csrf_exempt

from .models import Category, Product, User, Order
from .serializers import CategorySerializer, ProductSerializer, UserSerializer, OrderSerializer


class CategoryViewSet(viewsets.ViewSet):
    """
    A simple Viewset for viewing all categories
    """

    queryset = Category.objects.all()

    @extend_schema(responses=CategorySerializer)
    def list(self, request):
        serializer = CategorySerializer(self.queryset, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ViewSet):
    """
    A simple Viewset for viewing all products
    """

    queryset = Product.objects.all().is_active()

    lookup_field = "slug"

    def retrieve(self, request, slug=None):
        serializer = ProductSerializer(
            Product.objects.filter(slug=slug)
            .select_related("category")
            .prefetch_related(Prefetch("product_line"))
            .prefetch_related(Prefetch("product_line__product_image"))
            .prefetch_related(Prefetch("product_line__attribute_value__attribute"))
            , many=True,
        )
        data = Response(serializer.data)

        q = list(connection.queries)
        print(len(q))
        for qs in q:
            sqlformatted = format(str(qs["sql"]), reindent=True)
            print(highlight(sqlformatted, SqlLexer(), TerminalFormatter()))

        return data

    @extend_schema(responses=ProductSerializer)
    def list(self, request):
        serializer = ProductSerializer(self.queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=["get"],
        detail=False,
        url_path=r"category/(?P<slug>[\w-]+)",
    )
    def list_product_by_category_slug(self, request, slug=None):
        """
        An endpoint to return products by category
        """
        serializer = ProductSerializer(
            self.queryset.filter(category__slug=slug), many=True
        )
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @csrf_exempt
    @action(detail=False,
            methods=['post']
            )
    def create_order(self, request):
        username = request.data.get('username')
        pid = request.data.get('product_pid')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"warn": "user name not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            product = Product.objects.get(pid=pid)
        except Product.DoesNotExist:
            return Response({"warn": "product id not found"}, status=status.HTTP_404_NOT_FOUND)

        order = Order.objects.create(user=user, product=product)
        serializer = OrderSerializer(order)

        return Response({"message": "Order created successfully", "order": serializer.data},
                        status=status.HTTP_201_CREATED)
