from django.views.generic import View
from django.contrib.auth.decorators import login_required


class LoginRequiredViewMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        func = super().as_view(**initkwargs)
        # 装饰类视图
        return login_required(func)
