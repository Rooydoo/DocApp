"""医局人員管理アプリ - バックエンド"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import staff, hospitals, external_hospitals, careers, external_works, periods

# テーブル作成
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="医局人員管理API",
    description="医局の人員管理を行うAPIサーバー",
    version="1.0.0"
)

# CORS設定（Electron/React開発用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(staff.router)
app.include_router(hospitals.router)
app.include_router(external_hospitals.router)
app.include_router(careers.router)
app.include_router(external_works.router)
app.include_router(periods.router)


@app.get("/")
def root():
    """ヘルスチェック"""
    return {"status": "ok", "message": "医局人員管理API"}


@app.get("/api/positions")
def get_positions():
    """職種選択肢"""
    return ["専攻医", "助教", "講師", "准教授", "教授"]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
