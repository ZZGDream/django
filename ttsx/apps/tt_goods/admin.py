from django.contrib import admin
from .models import Goods,GoodsSKU,GoodsCategory,GoodsImage,IndexGoodsBanner,IndexCategoryGoodsBanner,IndexPromotionBanner
# Register your models here.
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(GoodsCategory)
admin.site.register(GoodsImage)
admin.site.register(IndexGoodsBanner)
admin.site.register(IndexCategoryGoodsBanner)
admin.site.register(IndexPromotionBanner)

# 用户：python 密码123
