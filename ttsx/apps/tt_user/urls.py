from django.conf.urls import url
from . import views

urlpatterns = [
    # url('register$',views.register)
    url(r'^register$',views.RegisterView.as_view()),
    url('^active/(.+)$',views.active),
    url('^exists$',views.exists),
    url('^login$',views.LoginView.as_view()),
    url('^logout',views.logout_user),
    url('^info$',views.info),
    url('^order$',views.order),
    url('^site$',views.SiteView.as_view()),
]

