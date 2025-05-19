from rest_framework.serializers import ModelSerializer
from api.models import Game, Player, Word
from rest_framework import serializers


class GameSerializer(ModelSerializer):
    class Meta:
        model = Game
        fields = ["difficulty"]


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
