from django.urls import include, path

from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers

from . import views

# router = SimpleRouter()
router = DefaultRouter()
router.register('products', views.ProductViewSet ,basename='product',)
router.register('categories', views.CategoryViewSet, basename='category',)
router.register('comments', views.CommentViewset , basename='comment',)
router.register('carts', views.CartViewSet,)

product_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
product_router.register('comments', views.CommentViewset, basename='product-comments')

cart_router = routers.NestedDefaultRouter(router, 'carts',  lookup='cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-itmes')

urlpatterns = router.urls + product_router.urls + cart_router.urls

# urlpatterns = [
#     path('', include(router.urls)),
# ]

# urlpatterns = [
#     # path('products/', views.product_list, name='product_list',),
#     # path('products/<int:pk>/', views.product_detail, name='product_detail',),
#     path('products/', views.ProductList.as_view(), name='product_list',),
#     path('products/<int:pk>/', views.ProductDetail.as_view(), name='product_detial',),

#     # path('categories/', views.category_list, name='category-list',),
#     # path('categories/<int:pk>/', views.category_detail, name='category-detail'),
#     path('categories/', views.CategoryList.as_view(), name='category_list',),
#     path('categories/<int:pk>/', views.CategoryDetail.as_view(), name='category_detail',),
    

# ]
