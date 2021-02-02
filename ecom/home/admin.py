from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Category,Maintaince,Item,Slider,Brand,Setting,Images,Order,OrderItem,Profile, Customer,Cart,CartItem,Comment,Riview

class SettingAdmin(admin.ModelAdmin):
    list_display=['title','company','update_at','status']

# Register your models here.
admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Item)
admin.site.register(Slider)
admin.site.register(Brand)
admin.site.register(Images)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Profile)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Riview)
admin.site.register(Setting, SettingAdmin)
admin.site.register(Comment, MPTTModelAdmin)
admin.site.register(Maintaince)