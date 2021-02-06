from django.contrib import admin
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from .models import Category,Maintaince,Item,Slider,Brand,Setting,Images,Order,OrderItem,Profile, Customer,Cart,CartItem,Comment,Riview, ShopCart

class SettingAdmin(admin.ModelAdmin):
    list_display=['title','company','update_at','status']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user_name','image_tag']



class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title',
                    'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug':('title',)}
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative product count
        qs = Category.objects.add_related_count(
                qs,
                Product,
                'category',
                'products_cumulative_count',
                cumulative=True)

        # Add non cumulative product count
        qs = Category.objects.add_related_count(qs,
                 Product,
                 'category',
                 'products_count',
                 cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.products_count
    related_products_count.short_description = 'Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count
    related_products_cumulative_count.short_description = 'Related products (in tree)'

class ItemImageInline(admin.TabularInline):
    model = Images
    extra = 5




class ItemAdmin(admin.ModelAdmin):
    list_display = ['title','category', 'status','image_tag','quantity']
    list_filter = ['category']
    readonly_fields = ('image_tag',)
    inlines = [ItemImageInline]
    prepopulated_fields = {'slug': ('title',)}

class OrderItemAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'item','price' ,'quantity','Total_Price']
    list_filter = ['user']

class ShopCartAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'item','price' ,'quantity','Total_Price']
    list_filter = ['user']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user','Items']
    
# Register your models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(Item,ItemAdmin)
admin.site.register(Slider)
admin.site.register(Brand)
admin.site.register(Images)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem,OrderItemAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Setting, SettingAdmin)
admin.site.register(Comment, MPTTModelAdmin)
admin.site.register(Maintaince)
admin.site.register(ShopCart,ShopCartAdmin)