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




class ProfileGameSerializer(serializers.ModelSerializer):
    opponent = serializers.SerializerMethodField()
    your_turn = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()
    can_start = serializers.SerializerMethodField()
    can_continue = serializers.SerializerMethodField()
    can_resume = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ['id', 'difficulty', 'status', 'masked_word', 'created_at', 'started_at',
                  'opponent', 'your_turn', 'result', 'can_start', 'can_continue', 'can_resume']

    def get_opponent(self, obj):
        user = self.context['request'].user
        if obj.player1 == user:
            return obj.player2.username if obj.player2 else None
        return obj.player1.username

    def get_your_turn(self, obj):
        user = self.context['request'].user
        return obj.turn == user if obj.status == 'active' else None

    def get_result(self, obj):
        if obj.status != 'finished':
            return None
        # برنده کسی است که کلمه را کامل حدس زده یا امتیاز بیشتر دارد
        # اینجا صرفاً نمونه ساده برگردانده شده:
        if obj.masked_word == obj.word:
            # اگر کلمه کامل حدس زده شده
            return 'win'
        else:
            return 'lose'

    def get_can_start(self, obj):
        user = self.context['request'].user
        return obj.status == 'waiting' and obj.player1 == user and obj.player2 is not None

    def get_can_continue(self, obj):
        user = self.context['request'].user
        return obj.status == 'active' and (obj.player1 == user or obj.player2 == user)

    def get_can_resume(self, obj):
        user = self.context['request'].user
        return obj.status == 'paused' and (obj.player1 == user or obj.player2 == user)
