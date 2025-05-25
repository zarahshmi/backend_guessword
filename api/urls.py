from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import RegisterAPIView, CreateGameAPIView, WaitingGamesAPIView, JoinGameAPIView, GuessLetterAPIView, \
    PauseGameAPIView, ResumeGameAPIView, ProfileAPIView, GameDetailAPIView

urlpatterns = [

    path('register/', RegisterAPIView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),

    path('profile/', ProfileAPIView.as_view()),

    path('create-game/', CreateGameAPIView.as_view()),
    path('waiting-games/', WaitingGamesAPIView.as_view()),
    path("games/<int:game_id>/join/", JoinGameAPIView.as_view()),

    path('games/<int:game_id>/guess/', GuessLetterAPIView.as_view()),

    path('games/<int:game_id>/pause/', PauseGameAPIView.as_view()),
    path('games/<int:game_id>/resume/', ResumeGameAPIView.as_view()),
    path('games/<int:game_id>/detail/', GameDetailAPIView.as_view()),

]

