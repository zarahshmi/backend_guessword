from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.models import Player,Word, Game
import random
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone


class RegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {
                    'error': 'Username and password are required!'
                }, status=400
            )

        if Player.objects.filter(username=username).exists():
            return Response(
                {
                    'error': 'This username has already been taken!'
                }, status=400
            )
        player = Player.objects.create_user(
            username=username,
            password=password
        )

        return Response(
            {
                'success': True,
                'user': {
                    'id': player.id,
                    'username': player.username
                }
            }, status=201
        )



class CreateGameAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        difficulty = request.data.get('difficulty')

        if difficulty not in ['easy', 'medium', 'hard']:
            return Response({'error': 'Invalid difficulty level'}, status=400)

        words = Word.objects.filter(difficulty=difficulty)
        if not words.exists():
            return Response({'error': 'No words found for this difficulty'}, status=400)

        word_obj = random.choice(list(words))
        real_word = word_obj.text.lower()
        masked_word = '_' * len(real_word)

        game = Game.objects.create(
            player1=request.user,
            word=real_word,
            masked_word=masked_word,
            difficulty=difficulty,
            status='waiting',
            turn=request.user
        )

        return Response({
            'game_id': game.id,
            'word_length': len(real_word),
            'difficulty': game.difficulty,
            'status': game.status
        }, status=201)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.models import Game

class WaitingGamesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        games = Game.objects.filter(
            status='waiting',
            player2__isnull=True
        ).exclude(player1=request.user)

        data = []
        for game in games:
            data.append({
                'game_id': game.id,
                'player1': game.player1.username,
                'difficulty': game.difficulty,
                'created_at': game.created_at,
            })

        return Response(data)

# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from api.models import Game
from api.serializers import GameSerializer



class JoinGameAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_id, *args, **kwargs):
        game = get_object_or_404(Game, id=game_id)

        if game.status != 'waiting':
            return Response({'error': 'You cannot join this game'}, status=400)

        if game.player1 == request.user:
            return Response({'error': 'You cannot join your own game'}, status=400)

        if game.player2:
            return Response({'error': 'Game already has two players'}, status=400)

        game.player2 = request.user
        game.status = 'active'
        game.started_at = timezone.now()
        game.save()

        serializer = GameSerializer(game)
        return Response(serializer.data, status=200)
