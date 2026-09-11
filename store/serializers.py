from django.utils.text import slugify

from decimal import Decimal
from rest_framework import serializers

from .models import Category, Order, OrderItem, Product
from store import models

DOLLARS_TO_TOMAN = 190000

class CategorySerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255,)
    description = serializers.CharField(max_length=500,)
    category_count = serializers.SerializerMethodField()


    class Meta:
        model = models.Category
        fields = ['title','description', 'category_count' ]

    def validate(self, data):
        if len(data['title']) < 3:
            raise serializers.ValidationError('the title must be at least 3 character')
        return data
    
    def get_category_count(self, category):
        return category.products.count()


class ProductSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    name = serializers.CharField(max_length=255,)
    price = serializers.DecimalField(max_digits=6,decimal_places=2, source='unit_price',)
    # inventory  = serializers.IntegerField()
    price_toman = serializers.SerializerMethodField()
    # price_after_tax = serializers.SerializerMethodField()
    # category = serializers.HyperlinkedRelatedField(
    #     queryset=Category.objects.all(),
    #     view_name='category-detail'
    # )
    # category = CategorySerializer()
    category = serializers.PrimaryKeyRelatedField(
        queryset = Category.objects.all()
    )

    class Meta:
        model = models.Product
        fields = ['name','price','category','inventory','slug','description','price_toman']

    def get_price_toman(self, product):
        return int(product.unit_price * DOLLARS_TO_TOMAN)
    
    # def get_price_after_tax(self, product):
    #     return product.unit_price * DOLLARS_TO_TOMAN * Decimal(1.09)

    def validate(self, data): # an example of validation for data
        if len(data['name']) < 6 :
            raise serializers.ValidationError('the length of the name should be at least 6 charachter.')
        return data
    
    def create(self, validated_data):
        product = models.Product(**validated_data)
        product.slug = slugify(product.name)
        product.save()
        return product

class CommentSerializer(serializers.ModelSerializer):   

    # product = serializers.PrimaryKeyRelatedField(
    #     queryset = models.Comment.objects.select_related('product').all()
    # )

    def create(self, validated_data):
        product_id = self.context['product_pk']
        return models.Comment.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = models.Comment
        fields = ['id','name','body',]

class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id','name','unit_price',]

class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ['id','product','quantity',]

    def create(self, validated_data):
        cart_id = self.context['cart_pk']

        product = validated_data.get('product')
        quantity = validated_data.get('quantity')

        try:
            cart_item = models.CartItem.objects.get(cart_id=cart_id,product_id=product.id)
            cart_item.quantity += quantity
            cart_item.save()
        except models.CartItem.DoesNotExist:
            cart_item = models.CartItem.objects.create(cart_id=cart_id, **validated_data)
        
        self.instance = cart_item

        return cart_item
    
class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta: 
        model = models.CartItem
        fields = ['quantity',]

class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer()
    item_total = serializers.SerializerMethodField()

    def get_item_total(self, cart_item):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = models.CartItem
        fields = ['id','product','quantity','item_total',]

class CartSerilizer(serializers.ModelSerializer): 
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

    class Meta:
        model = models.Cart
        fields = ['id','created_at','items','total_price',]
        read_only_fields = ['id',]
        
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = ['id','user','birth_date',]
        read_only_fields = ['user',]

class OrderItemProductSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Product 
        fields = ['id','name','unit_price',]

class OrderItemSerializer(serializers.ModelSerializer):

    product = OrderItemProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id','product','quantity','unit_price',]


class OrderSerializer(serializers.ModelSerializer):
     
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order 
        fields = ['id','customer_id','status','datetime_created','items',]
         

