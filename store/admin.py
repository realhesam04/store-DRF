from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from .models import Product, Category, Order, OrderItem, Customer, Comment, Discount,Cart,CartItem,Address


class InventoryFilter(admin.SimpleListFilter):
    LESS_THAN_3 = '<=3'
    BETWEEN_3_and_10 = '3<=10'
    MORE_THAN_10 = '<10'
    title = 'Critical Inventory Status'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            (InventoryFilter.LESS_THAN_3, 'Low'),
            (InventoryFilter.BETWEEN_3_and_10, 'Ok'),
            (InventoryFilter.MORE_THAN_10, 'High'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == InventoryFilter.LESS_THAN_3:
            return queryset.filter(inventory__lte=3)
        if self.value() == InventoryFilter.BETWEEN_3_and_10:
            return queryset.filter(inventory__gt=3, inventory__lte=10)
        if self.value() == InventoryFilter.MORE_THAN_10:
            return queryset.filter(inventory__gt=10)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'name',
                    'inventory',
                    'unit_price',
                    'inventory_status',
                    'product_category',
                    'num_of_comments',
                    ]
    list_per_page = 10
    list_editable = ['unit_price', 'inventory']
    list_select_related = ['category']
    list_filter = ['datetime_created', InventoryFilter]
    actions = ['clear_inventory',]
    prepopulated_fields = {
        'slug': ['name',]
    }
    search_fields = ['name',]

    @admin.display(ordering='inventory')
    def inventory_status(self, product: Product):
        if product.inventory > 50 :
            return 'High'
        if product.inventory < 10 :
            return 'Low'
        return 'Medium'
        
    @admin.display(ordering='category__title')
    def product_category(self, product: Product):
        return product.category.title
    
    def get_queryset(self, request):
        return super()\
                    .get_queryset(request)\
                    .prefetch_related('comments')\
                    .annotate(
                        comments_count=Count('comments')
                    )

    @admin.display(ordering='comments_count', description='# comments')
    def num_of_comments(self, product: Product):
        url = (
            reverse('admin:store_comment_changelist')
            + '?'
            + urlencode({
                'product__id': product.id
            })
        )
        return format_html('<a href="{}">{}</a>', url, product.comments_count)
    
    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{update_count} of products inventories cleared to 0.',
        )

class OrderItemInLine(admin.TabularInline):
    model = OrderItem
    fields = ['product','quantity','unit_price',]
    min_num = 1
    # extra = 1 
    # max_num = 10 # maximum number of order-item that an order can have

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','customer','status','datetime_created','num_of_items',]
    list_per_page = 10
    list_editable = ['status',]
    ordering = ['datetime_created',]
    inlines = [OrderItemInLine,]

    def get_queryset(self, request):
        return super().get_queryset(request)\
                    .prefetch_related('items')\
                    .annotate(
                        items_count=Count('items')
                    )
    
    @admin.display(ordering='items_count')
    def num_of_items(self, order):
        return order.items_count
 
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id','status','product',]
    list_editable = ['status']
    list_per_page = 10
    autocomplete_fields = ['product',]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id','order','product','quantity','unit_price',]
    autocomplete_fields = ['product',]

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id','first_name','last_name','email','phone_number','birth_date',]
    search_fields = ['first_name__istartswith','last_name__istartswith',]

    def first_name(self, customer):
        return customer.user.first_name
    
    def last_name(self, customer):
        return customer.user.last_name
    
    def email(self, customer):
        return customer.user.email
    

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['customer','province','city','street',]
    search_fields = ['customer__first_name__istartswith','customer__last_name__istartswith','province__istartswith',]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id','title','description',]

    def __str__(self):
        return f"{self.title}"
    

class CartItemInLine(admin.TabularInline):
    model = CartItem
    fields = ['id','product','quantity',]
    extra = 0
    min_num = 1

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id','created_at',] 
    inlines = [CartItemInLine,]