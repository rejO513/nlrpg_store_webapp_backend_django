# Neverland RPG コンテンツ販売 Webアプリケーション(バックエンド)

## Webアプリケーションの概要

### 開発期間
2023年9月～ (継続中)

### 開発環境
#### フロントエンド
JavaScript、React(Semantic UI、React Router DOM)、Nginx
#### バックエンド
Python、Django(Django REST Framework)、Nginx
#### インフラ
Linux、AWS、GCP、Docker

### 開発背景
開発目的は、時間コストを削減するためだ。従来、コンテンツ購入の決済処理をGoogleフォームで受け取り、それを人の目で確認して、手動で決済処理とコンテンツの適用を行っていた。中には、サブスクリプション型のコンテンツも存在するため、更新や解約処理に非常に時間を要していた。また、手動ではミスが発生する恐れもあるため、決済処理を自動化することで迅速かつ正確に手続きを行えると考えた。

### 現時点で実装済みの機能
- Googleアカウントを用いたユーザー登録・ログイン
- ユーザー情報の閲覧機能
- ユーザー情報(表示名、外部アカウントIDなど)を変更する機能

## バックエンドサーバーについて

フレームワーク: Django REST Framework

ライブラリ: Google OAuth

### エンドポイント

#### /verify-code
Authorization Code を id_token, access_tokenに変換

https://oauth2.googleapis.com/token にリクエストを送信

リクエストメッセージ:
- Authorization Code
- Google OAuth2 クライアントID
- Google OAuth2 クライアントシークレット
- リダイレクトURL

レスポンス:
- id_token
- access_token

#### /verify-token
id_tokenからGoogleアカウント情報を抽出する

id_token: JWT形式

Googleアカウント情報:
- メールアドレス
- ユーザー名
- アイコン

#### /register
ユーザー登録

必要事項:
username: ユーザー名
email: メールアドレス
image_url: ユーザーアイコン

上記データを元にユーザーモデルを作成
※ユーザーモデルの詳細は後述

#### /get-user-detail
ユーザー情報取得

ユーザー情報をJSON形式で返す

#### /user-data-update
ユーザー情報更新

JSON形式のユーザー情報を元に更新する

### ユーザーモデル
#### パラメータ
- email : メールアドレス
- username : 表示名
- discord_id : DiscordアカウントのID
- minecraft_accounts : 現在のユーザーに紐づけられている全てのMinecraftアカウント情報
- image_url : ユーザーアイコン
- is_staff : 管理者かどうか
- is_active : 有効なアカウントか
- date_joined : 登録日

### Minecraftアカウント情報について
MinecraftAccountクラスで管理

#### パラメータ
- mc_uuid : MinecraftアカウントのUUID
- edition : Minecraftアカウントのプラットフォーム (java or bedrock)
- total_donation : 寄付総額
- priority_access : 優先接続権の有無
- rank_plan : サブスクリプションプランの種類 (gold or jewelry)
- plan_start_date : サブスクリプションの開始日
- plan_end_date : サブスクリプションの終了日
- plan_change_date : サブスクリプションプランの変更予定日
- change_plan : 変更先のプラン
- used_donator_discount : Donator割引が使用済みか
- application_logs : 購入申請のログ(複数)

※優先接続権とは、サーバーが満員時でも接続可能な権利のこと

#### Minecraftアカウントのユーザー名,UUIDについて
Minecraftアカウントのユーザー名ではなく、UUIDで保持する理由は、ユーザー名は変更可能でUUIDは一意識別子であるというMinecraftの仕様に基づいている。

ユーザー情報取得時は、UUIDをWeb APIでユーザー名に変換して返している。

ユーザー情報更新時は、リクエストメッセージのユーザー名をWeb APIでUUIDに変更して保存している。

## 購入申請のログについて
Applicationクラスで管理

#### パラメータ
- confirm : システムが金額の受け取りを確認済みか
- price : 支払金額
- detail : 決済情報 (決済方法により異なる)
- purpose : 寄付金の用途
- type : 申請の種類
- donator_discount : Donator割引を使用するか
- plan_date : サブスクリプションの(開始,更新,変更,解約)日
- month : サブスクリプションの期間(月単位)
- apply_date : 申請日
- confirm_date : 受け取り確認日
