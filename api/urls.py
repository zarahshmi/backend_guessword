from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import RegisterAPIView, CreateGameAPIView, WaitingGamesAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('create-game/', CreateGameAPIView.as_view()),
    path('waiting-games/', WaitingGamesAPIView.as_view()),

]

