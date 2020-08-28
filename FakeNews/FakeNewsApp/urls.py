from django.urls import path
from . import views

urlpatterns = [
    path('', views.homeView, name='index'),
    path('login', views.loginView, name='loginView'),
    path('signup', views.signupView, name='signupView'),
    path('profile', views.profile, name='profile'),
    path('logout', views.logoutView, name='logoutView'),
    path('home', views.homeView, name='homeView'),
    path('article/<str:artid>', views.articleView, name="articleView"),
    path('uploadnew', views.articleUpload, name="articleUpload"),
    path('changestake', views.stakeView, name="stakeView"),
    path('auditing/<str:artid>', views.auditView, name="auditView"),
    path('resetblockchain2020blockforblock', views.restored_blockchain, name="restored_blockchain"),
    path('likeinterface', views.likeInterface, name="likeInterface"),
    path('postcomment', views.postComment, name="postComment"),
    path('latest', views.latestNews, name="latestNews"),
]
  
# editprofile
# inbox