from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager

class CustomUserManager(BaseUserManager):
	
	use_in_migrations = True

	def _create_user(self, request_data, password, **extra_fields):
		if not request_data['email']:
			raise ValueError('emailを入力してください')
		if not request_data['username']:
			raise ValueError('usernameを入力してください')
		email = self.normalize_email(request_data['email'])
		if self.filter(email=email).exists():
			raise ValueError('このemailはすでに使用されています。')
		user = self.model(
			username=request_data['username'],
			email=email,
			image_url=request_data['image_url'],
			**extra_fields
		)
		user.set_password(password)
		user.save(using=self.db)
		return user

	def create_user(self, request_data, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(request_data, password, **extra_fields)
	
	def create_superuser(self, username, email, password, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		if extra_fields.get('is_staff') is not True:
			raise ValueError('staffがTrueではないです')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('is_superuserがTrueではないです')
		if not email:
			raise ValueError('emailを入力してください')
		if not username:
			raise ValueError('usernameを入力してください')
		email = self.normalize_email(email)
		user = self.model(username=username, email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self.db)
		return user
	
class Application(models.Model):
	PURPOSE = (
		('anything', '用途を限定しない'),
		('server_cost', 'サーバー運用費'),
	)
	TYPE = (
		('rank_apply', 'ランク申し込み'),
		('rank_update', 'ランク更新'),
		('rank_continue', 'ランク継続'),
		('rank_cancel', 'ランク解約'),
		('donation', '寄付'),
	)
	# 受け取り確認済み
	confirm = models.BooleanField('Confirm', default=False)
	# 支払い金額
	price = models.IntegerField('DonationPrice', default=0)
	# 決済情報
	detail = models.CharField('PaymentDetail', max_length=64, null=True)
	# 寄付金の用途
	purpose = models.CharField('Purpose', choices=PURPOSE, max_length=16, null=True)
	# コンテンツの種類
	type = models.CharField('Type', choices=TYPE, max_length=16)
	# Donator割引
	donator_discount = models.BooleanField('DonatorDiscount', default=False)
	# 契約の(開始,更新,変更,解約)日
	plan_date = models.DateField('PlanStartDate', null=True)
	# 期間(月単位)
	month = models.IntegerField('Month', default=0)
	# 申請日
	apply_date = models.DateField('ApplyDate', null=True)
	# 確認日
	confirm_date = models.DateField('ConfirmDate', null=True)
	
class MinecraftAccount(models.Model):
	PLANS = (
		('gold', 'Gold'),
		('jewelry', 'Jewelry'),
	)
	EDITIONS = (
		('java', 'Java Edition'),
		('bedrock', 'Bedrock Edition'),
	)
	# MinecraftアカウントのUUID
	mc_uuid = models.UUIDField('UUID', unique=True, max_length=32, null=True)
	# Minecraftアカウントのプラットフォーム
	edition = models.CharField('Edition', choices=EDITIONS, max_length=16, null=True)
	# 寄付総額
	total_donation = models.IntegerField('TotalDonation', default=0)
	# 優先接続権の有無
	priority_access = models.BooleanField('PriorityAccess', default=False)
	# ランクプラン
	rank_plan = models.CharField('RankPlan', choices=PLANS, max_length=16, null=True)
	# 契約の開始日
	plan_start_date = models.DateField('PlanStartDate', null=True)
	# 契約の終了日
	plan_end_date = models.DateField('PlanEndDate', null=True)
	# プランの変更予定日
	plan_change_date = models.DateField('PlanChangeDate', null=True)
	# 変更先のプラン
	change_plan = models.CharField('ChangeRankPlan', choices=PLANS, max_length=16, null=True)
	# Donator割引使用済み
	used_donator_discount = models.BooleanField('UsedDonatorDiscount', default=False)
	# 申請ログ
	application_logs = models.ManyToManyField(Application, related_name='Application')
	

class CustomUser(AbstractBaseUser, PermissionsMixin):
	# unique=True は全てのユーザーのEmailが異なることを保証
	# blank=Trueは空でもよい

	# メールアドレス
	email = models.EmailField('Email', unique=True, null=True)
	# 表示名
	username = models.CharField('Display Name', max_length=150)
	# Discord ID
	discord_id = models.CharField('Discord ID', unique=True, max_length=32, null=True)
	# Minecraftの各アカウント
	minecraft_accounts = models.ManyToManyField(MinecraftAccount, related_name='Minecraft_Accounts')
	# ユーザーアイコン
	image_url = models.URLField('imageUrl', blank=True, max_length=200)
	is_staff = models.BooleanField('is_staff', default=False)
	is_active = models.BooleanField('is_active', default=True)
	date_joined = models.DateTimeField('date_joined', default=timezone.now)

	objects=CustomUserManager()

	# 必須
	USERNAME_FIELD = 'email'

	# 登録時に必要なフィールド
	REQUIRED_FIELDS = ['username']

	class Meta:
		verbose_name = "user"
		verbose_name_plural = "users"
