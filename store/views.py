from django.shortcuts import get_object_or_404
from django.db.models import Count

from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .pagination import DefaultPagination
from . import serializers
from . import models
from . import filters
from .permissions import IsAdminOrReadOnly, SendPrivateEmailToCustomerPermission

   
class ProductViewSet(ModelViewSet):
    """
        This view is for both ProductList & ProductDetail
    """
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.objects.select_related('category').all()
    filter_backends = [SearchFilter ,DjangoFilterBackend , OrderingFilter,]
    search_fields = ['name','category__title']
    ordering_fields = ['name','unit_price','inventory',]
    pagination_class = DefaultPagination
    # filterset_fields = ['category_id','inventory',]
    filterset_class = filters.ProductFilter

    # def get_queryset(self):
    #     queryset = models.Product.objects.all()
    #     category_id_parameter = self.request.query_params.get('category_id')
    #     if category_id_parameter is not None:
    #         queryset = queryset.filter(category_id=category_id_parameter)
    #     return queryset

    def destroy(self, request, pk):
        product = get_object_or_404(models.Product.objects.select_related('products').all(), pk=pk)
        if product.order_items.count() > 0:
            return Response({'error': 'There are some order items including this product, please reomve them first.'})
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CategoryViewSet(ModelViewSet):

    """
        This view is for both CategoryList & CategoryDetail
    """

    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.prefetch_related('products').all()
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, pk):
        category = get_object_or_404(models.Category.objects.prefetch_related('products').all(), pk=pk)
        if category.products.count() > 0:
            return Response({'error': 'there are some products related to this category, please delete them first.'})
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CommentViewset(ModelViewSet):
    serializer_class = serializers.CommentSerializer
    queryset = models.Comment.objects.select_related('product').all()

    def get_queryset(self):
        product_pk = self.kwargs['product_pk']
        return models.Comment.objects.filter(product_id=product_pk)
    
    def get_serializer_context(self):
        return {'product_pk': self.kwargs['product_pk']}
    
class CartViewSet(CreateModelMixin,
                   RetrieveModelMixin,
                   DestroyModelMixin,
                   GenericViewSet):
    serializer_class = serializers.CartSerilizer
    queryset = models.Cart.objects.prefetch_related('items__product').all()

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete',]
    
    # serializer_class = serializers.CartItemSerializer

    def get_queryset(self): 
        cart_pk = self.kwargs['cart_pk']
        return models.CartItem.objects.select_related('product').filter(cart_id=cart_pk).all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return serializers.UpdateCartItemSerializer
        return serializers.CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['cart_pk']}

class CustomerViewSet(ModelViewSet):
    serializer_class = serializers.CustomerSerializer
    queryset = models.Customer.objects.all()
    permission_classes = [IsAdminUser]


    @action(detail=False, methods=['GET','PUT',], permission_classes=[IsAuthenticated])
    def me(self, request):
        user_id = request.user.id 
        customer = models.Customer.objects.get(user_id=user_id)
        if request.method == 'GET':

            serializer = serializers.CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = serializers.CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        
    @action(detail=True,methods=['GET'],permission_classes=[SendPrivateEmailToCustomerPermission])
    def send_private_email(self, request, pk):
        return Response(
            f'Sending Private Email to Customer {pk}'
        )


# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     # Class-Based View (short virsion)
#     serializer_class = serializers.ProductSerializer
#     queryset = models.Product.objects.select_related('category').all()

#     def delete(self, request, pk):
#         product = get_object_or_404(models.Product.objects.select_related('category'), pk=pk)
#         if product.order_items.count() > 0:
#             return Response({'error': 'there is order items including this product, please remove them first. '})
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class ProductList(ListCreateAPIView):
#     serializer_class = serializers.ProductSerializer
#     queryset = models.Product.objects.select_related('category').all()

#     def get_serializer_context(self):
#         return {'request': self.request}
 
# class CategoryDetail(RetrieveUpdateDestroyAPIView):
#     # Class-Based View
#     serializer_class = serializers.CategorySerializer
#     queryset = models.Category.objects.prefetch_related('products').all()

#     def delete(self, request, pk):
#         category = get_object_or_404(models.Category.objects.prefetch_related('products').all(), pk=pk)
#         if category.products.count() > 0: 
#             return Response({'error': 'there are products related to this category, please remove them first.'})
#         category.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class CategoryList(ListCreateAPIView):
#     serializer_class = serializers.CategorySerializer
#     queryset = models.Category.objects.prefetch_related('products').all()

#     def get_serializer_context(self):
#         return {'request': self.request}
       
    # def get_serializer_class(self):
    #     return serializers.ProductSerializer
    
    # def get_queryset(self):
    #     return models.Product.objects.select_related('category').all()
    


# class ProductList(APIView):
#     # Class-Based View

#     def get(self, request):
#         products_queryset = models.Product.objects.select_related('category').all()
#         serialzer = serializers.ProductSerializer(products_queryset,
#                                                 many=True,
#                                                     context= {'request': request})
#         return Response(serialzer.data)
    
#     def post(self, request):
#         serializer = serializers.ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.validated_data
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# class ProductDetail(APIView):
#     # Class-Based View

#     def get(self, request, pk):
#         product_queryset = get_object_or_404(models.Product.objects.select_related('category').all(), pk=pk)
#         serializer = serializers.ProductSerializer(product_queryset, context={'request': request})
#         return Response(serializer.data)
    
#     def put(self, request, pk):
#         product_queryset = get_object_or_404(models.Product.objects.select_related('category').all(), pk=pk)
#         serilizer = serializers.ProductSerializer(product_queryset, data=request.data)
#         serilizer.is_valid(raise_exception=True)
#         serilizer.save()
#         return Response(serilizer.data)

#     def delete(self, request, pk):
#         product_queryset = get_object_or_404(models.Product.objects.select_related('category').all(), pk=pk)
#         if product_queryset.order_items.count() > 0:
#             return Response({'error': 'there are some order items including this product. please delete them first.'})
#         product_queryset.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['GET','POST'])
# def product_list(request):
#     # Functional View
#     if request.method == 'GET':
#         products_queryset = models.Product.objects.select_related('category').all()
#         serialzer = serializers.ProductSerializer(products_queryset,
#                                                 many=True,
#                                                     context= {'request': request})
#         return Response(serialzer.data)
    
#     elif request.method == 'POST':
#         serializer = serializers.ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.validated_data
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        # OR
        # if serializer.is_valid():
        #     serializer.validated_data
        #     return Response('Everythin is OK!')
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # return Response('All OK!')    

# @api_view(['GET','PUT','DELETE',])
# def product_detail(request, pk):
#         # Functional View
#         # try:
#         #     product = models.Product.objects.get(pk=pk)
#         # except models.Product.DoesNotExist:
#         #     return  Response(status=status.HTTP_403_FORBIDDEN)
#     product = get_object_or_404(models.Product.objects.select_related('category').all() , pk=pk)
#     if request.method == 'GET':

#         serializer = serializers.ProductSerializer(product, context= {'request': request})
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = serializers.ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         if product.order_items.count() > 0:
#             return Response({'error': 'there are some order items including this product, please delete them first'})
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

    

# class CategoryDetail(APIView):
#     # Class-Based View

#     def get(self, request, pk):
#         category = get_object_or_404(models.Category.objects.prefetch_related('products').all(), pk=pk)
#         serializer = serializers.CategorySerializer(category, context= {'request': request})
#         return Response(serializer.data)
    
#     def put(self, request, pk):
#         category = get_object_or_404(models.Category.objects.prefetch_related('products').all(), pk=pk)
#         serializer = serializers.CategorySerializer(category, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
    
#     def delete(self, request, pk):
#         category = get_object_or_404(models.Category.objects.prefetch_related('products').all(), pk=pk)
#         if category.products.count() > 0:
#             return Response({'error': 'there are some products related to this category, please delete them first.'})
#         category.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET','PUT','DELETE'])
# def category_detail(request, pk):

#     category = get_object_or_404(models.Category.objects.annotate(
#         products_count=Count('products')
#     ), pk=pk)

#     if request.method == 'GET':
#         serializer = serializers.CategorySerializer(category, context= {'request': request})
#         return Response(serializer.data)
    
#     elif request.method == 'PUT':
#         serializer = serializers.CategorySerializer(category, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
    
#     elif request.method == 'DELETE':
#         if category.products.count() > 0:
#             return Response({'error': 'there are some products related to this category, please delete them first.'})
#         category.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['GET','POST'])
# def category_list(request):
#     if request.method == 'GET':
#         # categories_queryset = models.Category.objects.prefetch_related('products').all()
#         categories_queryset = models.Category.objects.annotate(
#             products_count= Count('products')
#         ).all()
#         serializer = serializers.\
#             CategorySerializer(\
#                 categories_queryset,
#                     many=True,
#                     context= {'request': request}
#                     )
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = serializers.CategorySerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
# class CategoryList(APIView):
#     # Class-Based View

#     def get(self, request):
#         # categories_queryset = models.Category.objects.prefetch_related('products').all()
#         categories_queryset = models.Category.objects.prefetch_related('products').all()
#         serializer = serializers.\
#             CategorySerializer(\
#                 categories_queryset,
#                     many=True,
#                     context= {'request': request}
#                     )
#         return Response(serializer.data)
    
#     def post(self, request):
#         categories_queryset = models.Category.objects.prefetch_related('products').all()
#         serializer = serializers.CategorySerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # def get_serializer_class(self):
    #     return serializers.CategorySerializer
    
    # def get_queryset(self):
    #     return models.Category.objects.prefetch_related('products').all()