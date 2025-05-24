from rest_framework.serializers import ModelSerializer
from api.models import Game, Player, Word
from rest_framework import serializers


class GameSerializer(serializers.ModelSerializer):
    player1 = serializers.CharField(source='player1.username')
    player2 = serializers.CharField(source='player2.username', allow_null=True)
    current_turn = serializers.CharField(source='turn.username', allow_null=True)

    class Meta:
        model = Game
        fields = ['id', 'player1', 'player2', 'word', 'masked_word',
                  'difficulty', 'status', 'created_at', 'started_at',
                  'current_turn']


class GameCreateSerializer(serializers.Serializer):
    difficulty = serializers.ChoiceField(choices=['easy', 'medium', 'hard'])



class WaitingGameSerializer(serializers.ModelSerializer):
    player1 = serializers.CharField(source='player1.username')

    class Meta:
        model = Game
        fields = ['id', 'player1', 'difficulty', 'created_at']


class GameListSerializer(ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'



class PlayerSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'



class WordSerializer(ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'
