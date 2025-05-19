from rest_framework.serializers import ModelSerializer

from api.models import Game, Player


class GameSerializer(ModelSerializer):
    class Meta:
        model = Game
        fields = ["difficulty"]


class GameListSerializer(ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class PlayerSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'
