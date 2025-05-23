from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.models import Player, Word, Game, Guess
import random
from django.utils import timezone
from api.serializers import GameCreateSerializer, WaitingGameSerializer,GameSerializer,GameListSerializer
from django.shortcuts import get_object_or_404



class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
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
    serializer_class = GameCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        difficulty = serializer.validated_data['difficulty']
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




class WaitingGamesAPIView(APIView):
    serializer_class = WaitingGameSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        games = Game.objects.filter(
            status='waiting',
            player2__isnull=True
        ).exclude(player1=request.user)

        serializer = self.serializer_class(games, many=True)
        return Response(serializer.data)




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

        game.turn = random.choice([game.player1, game.player2])
        game.save()

        serializer = GameSerializer(game)
        return Response(serializer.data, status=200)



class GuessLetterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_id):
        letter = request.data.get('letter', '').lower()
        if not letter or len(letter) != 1 or not letter.isalpha():
            return Response({'error': 'Invalid letter'}, status=400)

        game = get_object_or_404(Game, id=game_id)

        if game.status != 'active':
            return Response({'error': 'Game is not active'}, status=400)

        if game.turn != request.user:
            return Response({'error': 'It is not your turn'}, status=403)

        if letter in game.masked_word or letter in [g.letter for g in game.guesses.all()]:
            return Response({'error': 'Letter already guessed'}, status=400)

        real_word = game.word
        masked = list(game.masked_word)
        correct = False

        for i, c in enumerate(real_word):
            if c == letter:
                masked[i] = letter
                correct = True

        Guess.objects.create(game=game, player=request.user, letter=letter, correct=correct)

        game.masked_word = ''.join(masked)

        if correct:
            request.user.score += 20
        else:
            request.user.score = max(0, request.user.score - 20)

        request.user.save()

        if game.masked_word == game.word:
            game.status = 'finished'
        else:
            game.turn = game.player2 if game.turn == game.player1 else game.player1

        game.save()

        return Response({
            'masked_word': game.masked_word,
            'correct': correct,
            'next_turn': game.turn.username if game.status != 'finished' else None,
            'game_status': game.status,
            'your_score': request.user.score
        })




class PauseGameAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)

        if request.user != game.player1 and request.user != game.player2:
            return Response({'error': 'You are not part of this game'}, status=403)

        if game.status != 'active':
            return Response({'error': 'Game is not active'}, status=400)

        game.status = 'paused'
        game.save()
        return Response({'message': 'Game paused'}, status=200)



class ResumeGameAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)

        if request.user != game.player1 and request.user != game.player2:
            return Response({'error': 'You are not part of this game'}, status=403)

        if game.status != 'paused':
            return Response({'error': 'Game is not paused'}, status=400)

        game.status = 'active'
        game.save()
        return Response({'message': 'Game resumed'}, status=200)



from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, F
from api.models import Game
from api.serializers import ProfileGameSerializer

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        all_games = Game.objects.filter(Q(player1=user) | Q(player2=user)).order_by('-started_at')

        finished_games = all_games.filter(status='finished')
        paused_games = all_games.filter(status='paused')
        created_waiting_games = all_games.filter(player1=user, status='waiting')
        active_games = all_games.filter(status='active')
        joined_games = all_games.filter(player2=user)

        total_games = finished_games.count()
        wins = finished_games.filter(masked_word=F('word'), turn=user).count()
        losses = total_games - wins
        win_rate = round((wins / total_games) * 100, 2) if total_games > 0 else 0.0

        return Response({
            'id': user.id,
            'username': user.username,
            'score': user.score,
            'games_played': total_games,
            'wins': wins,
            'losses': losses,
            'win_rate': f"{win_rate}%",
            'created_waiting_games': ProfileGameSerializer(created_waiting_games, many=True, context={'request': request}).data,
            'active_games': ProfileGameSerializer(active_games, many=True, context={'request': request}).data,
            'paused_games': ProfileGameSerializer(paused_games, many=True, context={'request': request}).data,
            'joined_games': ProfileGameSerializer(joined_games, many=True, context={'request': request}).data,
            'finished_games': ProfileGameSerializer(finished_games, many=True, context={'request': request}).data,
        })

# views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from api.models import Game
from api.serializers import GameSerializer

class GameDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, game_id):
        user = request.user
        game = get_object_or_404(Game, id=game_id)

        if game.player1 != user and game.player2 != user:
            return Response({'detail': 'شما به این بازی دسترسی ندارید.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = GameSerializer(game)
        return Response(serializer.data)
