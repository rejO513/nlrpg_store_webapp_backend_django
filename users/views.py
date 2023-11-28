from .models import CustomUser
from django.db import transaction
from rest_framework import permissions, status, generics
from rest_framework.views import APIView #
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from google.oauth2 import id_token
from google.auth.transport import requests as requests_auth
import requests
from decouple import config
from .serializers import RegisterUserSerializer, UserSerializer
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.http import QueryDict

# MCIDをUUIDに変換する関数
def convert_mcid_to_uuid(mcid):
    response = requests.get('https://api.mojang.com/users/profiles/minecraft/'+mcid)
    if response.status_code == 200:
        return response.json().get('id')
    else:
        return None

# UUIDをMCIDに変換する関数
def convert_uuid_to_mcid(uuid):
    response = requests.get('https://sessionserver.mojang.com/session/minecraft/profile/'+uuid)
    if response.status_code == 200:
        return response.json().get('name')
    else:
        return None

# ユーザーデータ更新
class UserDataUpdate(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        logger = logging.getLogger(__name__)
        try:
            # logger.info(request.data)
            data = request.data.copy()

            minecraft_accounts = data.get('minecraft_accounts')
            for account in minecraft_accounts:
                mcid = account.pop('mcid')
                mc_uuid = convert_mcid_to_uuid(mcid)
                account['mc_uuid'] = mc_uuid
            user = CustomUser.objects.get(email=data['email'])
            serializer = UserSerializer(user, data=data)
            if serializer.is_valid():
                # update関数が実行される
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ユーザー情報取得
class GetUserDetail(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    def get(self, request):
        serializer = UserSerializer(request.user)
        data = serializer.data.copy()
        minecraft_accounts = data.get('minecraft_accounts')
        for account in minecraft_accounts:
            mc_uuid = account.pop('mc_uuid')
            mcid = convert_uuid_to_mcid(mc_uuid)
            account['mcid'] = mcid
        return Response(data)

# ユーザー登録
class RegisterUser(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = RegisterUserSerializer
    
    @transaction.atomic
    def post(self, request):
        logger = logging.getLogger(__name__)
        try:
            serializer = RegisterUserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error('Error: ', e)

# id_token から Googleアカウント情報を取得
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verifyToken(request):
    try:
        req = requests_auth.Request()
        token = request.data['id_token']
        audience = config("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
        user_google_info = id_token.verify_oauth2_token(token, req, audience)
        return Response(user_google_info, status=status.HTTP_200_OK)
    except KeyError:
        return Response({"error": "tokenId is missing in the request data."}, status=400)

# Authorization Code を id_token, accessTokenに変換
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verifyCode(request):
    try:
        # クライアント情報を設定
        client_id = config("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
        client_secret = config("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")
        # redirect_uri = 'http://ec.neverland-rpg.online'
        redirect_uri = 'http://localhost:3000'
        # authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
        token_url = 'https://oauth2.googleapis.com/token'

        # authorization_codeを取得
        authorization_code = request.data['code']

        # POSTリクエストのボディに含めるパラメータ
        payload = {
            'code': authorization_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }

        # トークンを取得するためのPOSTリクエストを送信
        response = requests.post(token_url, data=payload)

        return Response(response.json(), status=status.HTTP_200_OK)
    except KeyError:
        return Response({"error": "tokenId is missing in the request data."}, status=400)