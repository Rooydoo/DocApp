"""
Google Sheets APIサービス
"""
import os
import pickle
from typing import Optional, List, Dict, Any
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config.settings import settings
from config.constants import SheetsScopes
from utils.logger import get_logger
from utils.exceptions import APIException

logger = get_logger(__name__)


class GoogleSheetsException(APIException):
    """Google Sheets API例外"""
    pass


class GoogleSheetsService:
    """
    Google Sheets APIサービス

    スプレッドシートの作成、読み取り、書き込み機能を提供
    """

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Args:
            credentials_path: 認証情報ファイルのパス（省略時は設定から取得）
        """
        self.credentials_path = credentials_path or settings.google_sheets_credentials_path
        self.token_path = str(settings.credentials_dir / "sheets_token.pickle")
        self.scopes = SheetsScopes.all()
        self._service = None
        self._drive_service = None

    def _get_credentials(self) -> Credentials:
        """
        認証情報を取得

        Returns:
            Credentials: 認証情報
        """
        creds = None

        # 既存のトークンを読み込み
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # 有効な認証情報がない場合は新規取得
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Failed to refresh token: {e}")
                    creds = None

            if not creds:
                if not os.path.exists(self.credentials_path):
                    raise GoogleSheetsException(
                        f"認証情報ファイルが見つかりません: {self.credentials_path}\n"
                        "Google Cloud Consoleから認証情報をダウンロードしてください。"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.scopes
                )
                creds = flow.run_local_server(port=0)

            # トークンを保存
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        return creds

    def _get_service(self):
        """Sheets APIサービスを取得"""
        if self._service is None:
            creds = self._get_credentials()
            self._service = build('sheets', 'v4', credentials=creds)
        return self._service

    def _get_drive_service(self):
        """Drive APIサービスを取得（共有設定用）"""
        if self._drive_service is None:
            creds = self._get_credentials()
            self._drive_service = build('drive', 'v3', credentials=creds)
        return self._drive_service

    def create_spreadsheet(
        self,
        title: str,
        sheets: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        スプレッドシートを作成

        Args:
            title: スプレッドシートのタイトル
            sheets: シート定義のリスト [{"title": "シート名"}, ...]

        Returns:
            str: 作成されたスプレッドシートID
        """
        try:
            service = self._get_service()

            spreadsheet_body = {
                'properties': {'title': title}
            }

            if sheets:
                spreadsheet_body['sheets'] = [
                    {'properties': {'title': s.get('title', f'シート{i+1}')}}
                    for i, s in enumerate(sheets)
                ]

            spreadsheet = service.spreadsheets().create(
                body=spreadsheet_body,
                fields='spreadsheetId'
            ).execute()

            spreadsheet_id = spreadsheet.get('spreadsheetId')
            logger.info(f"Created spreadsheet: {spreadsheet_id}")

            return spreadsheet_id

        except HttpError as e:
            logger.error(f"Failed to create spreadsheet: {e}")
            raise GoogleSheetsException(f"スプレッドシートの作成に失敗しました: {e}")

    def get_spreadsheet_url(self, spreadsheet_id: str) -> str:
        """
        スプレッドシートのURLを取得

        Args:
            spreadsheet_id: スプレッドシートID

        Returns:
            str: URL
        """
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

    def write_data(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List[Any]],
        value_input_option: str = "USER_ENTERED"
    ) -> int:
        """
        データを書き込み

        Args:
            spreadsheet_id: スプレッドシートID
            range_name: 範囲（例: "シート1!A1:C10"）
            values: 書き込むデータ（2次元配列）
            value_input_option: 入力オプション（USER_ENTERED/RAW）

        Returns:
            int: 更新されたセル数
        """
        try:
            service = self._get_service()

            body = {'values': values}

            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body
            ).execute()

            updated_cells = result.get('updatedCells', 0)
            logger.info(f"Updated {updated_cells} cells in {spreadsheet_id}")

            return updated_cells

        except HttpError as e:
            logger.error(f"Failed to write data: {e}")
            raise GoogleSheetsException(f"データの書き込みに失敗しました: {e}")

    def read_data(
        self,
        spreadsheet_id: str,
        range_name: str
    ) -> List[List[Any]]:
        """
        データを読み取り

        Args:
            spreadsheet_id: スプレッドシートID
            range_name: 範囲（例: "シート1!A1:C10"）

        Returns:
            List[List[Any]]: 読み取ったデータ（2次元配列）
        """
        try:
            service = self._get_service()

            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])
            logger.info(f"Read {len(values)} rows from {spreadsheet_id}")

            return values

        except HttpError as e:
            logger.error(f"Failed to read data: {e}")
            raise GoogleSheetsException(f"データの読み取りに失敗しました: {e}")

    def append_data(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List[Any]]
    ) -> int:
        """
        データを追加（既存データの末尾に）

        Args:
            spreadsheet_id: スプレッドシートID
            range_name: 範囲（例: "シート1!A:C"）
            values: 追加するデータ（2次元配列）

        Returns:
            int: 追加された行数
        """
        try:
            service = self._get_service()

            body = {'values': values}

            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body
            ).execute()

            updates = result.get('updates', {})
            updated_rows = updates.get('updatedRows', 0)
            logger.info(f"Appended {updated_rows} rows to {spreadsheet_id}")

            return updated_rows

        except HttpError as e:
            logger.error(f"Failed to append data: {e}")
            raise GoogleSheetsException(f"データの追加に失敗しました: {e}")

    def format_cells(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        requests: List[Dict]
    ):
        """
        セルの書式を設定

        Args:
            spreadsheet_id: スプレッドシートID
            sheet_id: シートID
            requests: フォーマットリクエストのリスト
        """
        try:
            service = self._get_service()

            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()

            logger.info(f"Formatted cells in {spreadsheet_id}")

        except HttpError as e:
            logger.error(f"Failed to format cells: {e}")
            raise GoogleSheetsException(f"セルの書式設定に失敗しました: {e}")

    def add_data_validation(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        start_row: int,
        end_row: int,
        column: int,
        values: List[str]
    ):
        """
        ドロップダウンリスト（データ検証）を追加

        Args:
            spreadsheet_id: スプレッドシートID
            sheet_id: シートID
            start_row: 開始行（0から）
            end_row: 終了行
            column: 列（0から）
            values: 選択肢のリスト
        """
        try:
            service = self._get_service()

            request = {
                'setDataValidation': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': start_row,
                        'endRowIndex': end_row,
                        'startColumnIndex': column,
                        'endColumnIndex': column + 1
                    },
                    'rule': {
                        'condition': {
                            'type': 'ONE_OF_LIST',
                            'values': [{'userEnteredValue': v} for v in values]
                        },
                        'showCustomUi': True,
                        'strict': True
                    }
                }
            }

            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': [request]}
            ).execute()

            logger.info(f"Added data validation to {spreadsheet_id}")

        except HttpError as e:
            logger.error(f"Failed to add data validation: {e}")
            raise GoogleSheetsException(f"データ検証の追加に失敗しました: {e}")

    def share_spreadsheet(
        self,
        spreadsheet_id: str,
        email: str,
        role: str = "writer"
    ):
        """
        スプレッドシートを共有

        Args:
            spreadsheet_id: スプレッドシートID
            email: 共有先メールアドレス
            role: 権限（reader/writer/owner）
        """
        try:
            drive_service = self._get_drive_service()

            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }

            drive_service.permissions().create(
                fileId=spreadsheet_id,
                body=permission,
                sendNotificationEmail=True
            ).execute()

            logger.info(f"Shared spreadsheet {spreadsheet_id} with {email}")

        except HttpError as e:
            logger.error(f"Failed to share spreadsheet: {e}")
            raise GoogleSheetsException(f"スプレッドシートの共有に失敗しました: {e}")

    def get_sheet_id(self, spreadsheet_id: str, sheet_name: str) -> Optional[int]:
        """
        シート名からシートIDを取得

        Args:
            spreadsheet_id: スプレッドシートID
            sheet_name: シート名

        Returns:
            int: シートID、見つからない場合はNone
        """
        try:
            service = self._get_service()

            spreadsheet = service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()

            for sheet in spreadsheet.get('sheets', []):
                if sheet['properties']['title'] == sheet_name:
                    return sheet['properties']['sheetId']

            return None

        except HttpError as e:
            logger.error(f"Failed to get sheet ID: {e}")
            raise GoogleSheetsException(f"シートIDの取得に失敗しました: {e}")


# グローバルインスタンス
google_sheets_service = GoogleSheetsService()
