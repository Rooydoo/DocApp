"""データベース接続設定"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def get_data_dir():
    """データ保存ディレクトリを取得"""
    if getattr(sys, 'frozen', False):
        # ビルド後: ユーザーのホームディレクトリに保存
        data_dir = os.path.join(os.path.expanduser("~"), ".medical-office")
    else:
        # 開発中: backendディレクトリ内
        data_dir = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(data_dir, exist_ok=True)
    return data_dir


DATA_DIR = get_data_dir()
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'medical_office.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """DBセッション取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
