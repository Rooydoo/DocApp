"""
Google Sheets API サービス
スプレッドシートの作成・読み取り・書き込みを管理
"""
import os
from typing import Optional, List, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config.constants import SheetsScopes
from services.config_service import config_service
from utils.logger import get_logger
from utils.exceptions import APIException

logger = get_logger(__name__)

TOKEN_FILE = "config/credentials/sheets_token.json"


class GoogleSheetsService:
    """
    Google Sheets API クライアント

    使用例:
        service = GoogleSheetsService()
        if service.authenticate():
            url = service.create_spreadsheet("集計レポート", [
                {"title": "病院希望", "headers": ["職員名", "第1希望", ...], "rows": [...]},
            ])
    """

    def __init__(self):
        self.creds: Optional[Credentials] = None
        self.service = None
        self.credentials_path = config_service.get(
            config_service.Keys.GOOGLE_SHEETS_CREDENTIALS_PATH,
            "config/credentials/sheets_credentials.json"
        )

    def authenticate(self) -> bool:
        """
        OAuth2認証を実行

        Returns:
            bool: 認証成功時True
        """
        try:
            # 既存トークンの読み込み
            if os.path.exists(TOKEN_FILE):
                self.creds = Credentials.from_authorized_user_file(
                    TOKEN_FILE, SheetsScopes.all()
                )

            # トークンが無効または期限切れの場合
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        logger.error(f"Credentials file not found: {self.credentials_path}")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SheetsScopes.all()
                    )
                    self.creds = flow.run_local_server(port=0)

                # トークンを保存
                os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
                with open(TOKEN_FILE, "w") as token:
                    token.write(self.creds.to_json())

            self.service = build("sheets", "v4", credentials=self.creds)
            logger.info("Google Sheets API authenticated successfully")
            return True

        except Exception as e:
            logger.error(f"Google Sheets authentication failed: {e}")
            return False

    def is_authenticated(self) -> bool:
        """認証済みかどうかを確認"""
        return self.service is not None

    def create_spreadsheet(
        self,
        title: str,
        sheets_data: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        スプレッドシートを作成してデータを書き込む

        Args:
            title: スプレッドシート名
            sheets_data: シートデータのリスト
                [
                    {
                        "title": "シート名",
                        "headers": ["列1", "列2", ...],
                        "rows": [["値1", "値2", ...], ...]
                    },
                    ...
                ]

        Returns:
            スプレッドシートのURL（失敗時None）
        """
        if not self.is_authenticated():
            logger.error("Not authenticated. Call authenticate() first.")
            return None

        try:
            # スプレッドシート作成
            sheet_properties = []
            for i, sheet in enumerate(sheets_data):
                sheet_properties.append({
                    "properties": {
                        "title": sheet["title"],
                        "index": i
                    }
                })

            spreadsheet_body = {
                "properties": {"title": title},
                "sheets": sheet_properties
            }

            spreadsheet = self.service.spreadsheets().create(
                body=spreadsheet_body
            ).execute()

            spreadsheet_id = spreadsheet["spreadsheetId"]
            spreadsheet_url = spreadsheet["spreadsheetUrl"]

            logger.info(f"Spreadsheet created: {title} ({spreadsheet_id})")

            # 各シートにデータを書き込み
            for sheet in sheets_data:
                self._write_sheet_data(spreadsheet_id, sheet)

            # 書式設定を適用
            self._apply_formatting(spreadsheet_id, sheets_data)

            return spreadsheet_url

        except Exception as e:
            logger.error(f"Failed to create spreadsheet: {e}")
            raise APIException(f"スプレッドシートの作成に失敗しました: {e}")

    def _write_sheet_data(self, spreadsheet_id: str, sheet_data: Dict[str, Any]):
        """シートにデータを書き込む"""
        sheet_title = sheet_data["title"]
        headers = sheet_data.get("headers", [])
        rows = sheet_data.get("rows", [])

        # ヘッダー + データ行
        values = []
        if headers:
            values.append(headers)
        values.extend(rows)

        if not values:
            return

        body = {"values": values}

        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_title}'!A1",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        logger.info(f"Wrote {len(rows)} rows to sheet '{sheet_title}'")

    def _apply_formatting(self, spreadsheet_id: str, sheets_data: List[Dict[str, Any]]):
        """ヘッダー行に書式設定を適用"""
        requests = []

        for i, sheet in enumerate(sheets_data):
            if not sheet.get("headers"):
                continue

            # ヘッダー行を太字・背景色付きに
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": i,
                        "startRowIndex": 0,
                        "endRowIndex": 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 0.2,
                                "green": 0.4,
                                "blue": 0.85
                            },
                            "textFormat": {
                                "bold": True,
                                "foregroundColor": {
                                    "red": 1.0,
                                    "green": 1.0,
                                    "blue": 1.0
                                }
                            }
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat)"
                }
            })

            # 列幅の自動調整
            requests.append({
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": i,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": len(sheet["headers"])
                    }
                }
            })

            # ヘッダー行を固定
            requests.append({
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": i,
                        "gridProperties": {
                            "frozenRowCount": 1
                        }
                    },
                    "fields": "gridProperties.frozenRowCount"
                }
            })

        if requests:
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": requests}
            ).execute()


# シングルトンインスタンス
google_sheets_service = GoogleSheetsService()
