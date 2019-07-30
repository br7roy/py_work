"""HelloWorld URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    # path('admin/', admin.site.urls),
]

from django.conf.urls import url
from django.urls import path
from django.urls import include,re_path

from . import view,testdb,articledb,gendata,search

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', view.hello),
    # path('hello/',view.hello),
    # re_path(r'^$',include('view.hello')),
    url(r'^testdb$', testdb.testdb),
    url(r'^querydb$', testdb.insertdb),
    url(r'^updatedb$', testdb.updatedb),
    url(r'^deletedb$', testdb.deletedb),
    url(r'^articledb$', articledb.testdb),
    url(r'^gendata$',gendata.gendata),
    url(r'^search-form$',search.search_form),
    url(r'^search$',search.search),
    url(r'^search-post$',search.search_post)

]
# handler404 = view.page_not_found #改动2

