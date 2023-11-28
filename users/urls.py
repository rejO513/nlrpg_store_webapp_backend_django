from django.urls import path, include
from . import views
from .views import RegisterUser, GetUserDetail, UserDataUpdate

urlpatterns = [
    # id_tokenからGoogleアカウント情報を抽出
    path('verify-token/', views.verifyToken, name='verify-token'),
    # Authorization Code を id_token, access_tokenに変換
    path('verify-code/', views.verifyCode, name='verify-code'),
    # ユーザー登録
    path('register/', RegisterUser.as_view(), name='register'), 
    # ユーザー情報取得
    path('get-user-detail/', GetUserDetail.as_view(), name='get-user-detail'),
    # ユーザー情報更新
    path('user-data-update/', UserDataUpdate.as_view(), name='user-data-update'),
]

