from rest_framework import serializers
from .models import CustomUser, MinecraftAccount
import requests
import logging

class MinecraftAccountSerializer(serializers.Serializer):
	EDITIONS = (
		('java', 'Java Edition'),
		('bedrock', 'Bedrock Edition'),
	)
	# MinecraftアカウントID
	mc_uuid = serializers.UUIDField()
	# Minecraftアカウントのプラットフォーム
	edition = serializers.ChoiceField(choices=EDITIONS)

class UserSerializer(serializers.HyperlinkedModelSerializer):
    minecraft_accounts = MinecraftAccountSerializer(many=True)

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'username',
            'discord_id',
            'minecraft_accounts',
            'image_url',
        ]
        
    def update(self, instance, validated_data):
        logger = logging.getLogger(__name__)
        logger.info(validated_data)

        if 'minecraft_accounts' in validated_data:
            minecraft_accounts_data = validated_data.pop('minecraft_accounts')

            # MinecraftAccount のインスタンスのリストを作成
            minecraft_account_instances = []
            for account_data in minecraft_accounts_data:
                mc_uuid = account_data.get('mc_uuid')
                edition = account_data.get('edition')

                # MinecraftAccount インスタンスを取得または作成
                account, created = MinecraftAccount.objects.get_or_create(
                    mc_uuid=mc_uuid,
                    defaults={'edition': edition}
                )
                minecraft_account_instances.append(account)

            instance.minecraft_accounts.set(minecraft_account_instances)

        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.discord_id = validated_data.get('discord_id', instance.discord_id)
        instance.image_url = validated_data.get('image_url', instance.image_url)
        instance.save()
        return instance

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'image_url']
    
    def create(self, validated_data):
        request_data = validated_data
        return CustomUser.objects.create_user(request_data)
