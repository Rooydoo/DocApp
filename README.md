# 医局人員管理アプリ

医局長が医局の人員を管理するためのデスクトップアプリケーション。

## 機能

- 職員管理（姓名分離、職種、評価メモ）
- 病院管理（勤務先、外勤可否設定）
- 外勤病院管理
- 経歴管理（3ヶ月単位、入局前履歴対応）
- 外勤管理（表形式、最大3コマ、頻度パターン対応）
- シフト確認

## 技術スタック

- **フロントエンド**: React + TypeScript + Vite
- **バックエンド**: Python + FastAPI
- **データベース**: SQLite
- **デスクトップ**: Electron

## セットアップ

### バックエンド

```bash
cd backend
pip install -r requirements.txt
python main.py
```

サーバーが http://localhost:8000 で起動します。

### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

開発サーバーが http://localhost:5173 で起動します。

### Electron開発

```bash
cd frontend
npm run electron:dev
```

### ビルド

```bash
cd frontend
npm run electron:build
```

## API

- `GET /api/staff` - 職員一覧
- `GET /api/hospitals` - 病院一覧
- `GET /api/external-hospitals` - 外勤病院一覧
- `GET /api/careers` - 経歴一覧
- `GET /api/external-works` - 外勤一覧
- `GET /api/periods` - 期間選択肢
