import gspread
from google.oauth2.service_account import Credentials
import json
import streamlit as st
from datetime import datetime


def get_current_season():
    """Get current season year"""
    # NFL season runs Sept-Feb, so Jan-Feb should use previous year
    # You can manually override this if needed
    current_date = datetime.now()

    # If we're in January or February, use previous year (season started in previous year)
    if current_date.month <= 2:
        return current_date.year - 1
    else:
        return current_date.year


@st.cache_resource
def get_sheets_client():
    """Initialize Google Sheets client"""
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    try:
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Failed to initialize Google Sheets client: {e}")
        return None


class LeagueStorage:
    """Handle all persistent storage operations"""

    def __init__(self, season=None):
        self.client = get_sheets_client()
        self.season = season or get_current_season()

        if self.client:
            try:
                self.spreadsheet = self.client.open("SBS_League_Data")
            except gspread.SpreadsheetNotFound:
                st.error(
                    "Could not find 'SBS_League_Data' spreadsheet. Make sure it's shared with your service account.")
                self.spreadsheet = None
        else:
            self.spreadsheet = None

    def _get_worksheet_name(self, base_name):
        """Get worksheet name with season suffix"""
        return f"{base_name}_{self.season}"

    def save_playoff_matchups(self, matchups):
        """Save all playoff matchups for current season"""
        if not self.spreadsheet:
            st.error("Spreadsheet not initialized")
            return False

        try:
            worksheet_name = self._get_worksheet_name("playoff_matchups")

            # Try to get worksheet, create if doesn't exist
            try:
                sheet = self.spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                sheet = self.spreadsheet.add_worksheet(title=worksheet_name, rows=100, cols=10)

            sheet.clear()
            # Convert to JSON and save in A1
            sheet.update('A1', [[json.dumps(matchups)]])
            return True
        except Exception as e:
            st.error(f"Failed to save playoff matchups: {e}")
            return False

    def load_playoff_matchups(self):
        """Load all playoff matchups for current season"""
        if not self.spreadsheet:
            st.warning("Spreadsheet not initialized, using empty data")
            return {}

        try:
            worksheet_name = self._get_worksheet_name("playoff_matchups")
            sheet = self.spreadsheet.worksheet(worksheet_name)
            data = sheet.get('A1')

            if data and data[0] and data[0][0]:
                matchups = json.loads(data[0][0])
                # Convert string keys back to integers
                return {int(k): v for k, v in matchups.items()}
            return {}
        except gspread.WorksheetNotFound:
            # Worksheet doesn't exist yet for this season - this is normal
            return {}
        except Exception as e:
            st.warning(f"Could not load playoff matchups: {e}")
            return {}

    def save_custom_schedule(self, schedule_data):
        """Save custom schedule configuration for current season"""
        if not self.spreadsheet:
            return False

        try:
            worksheet_name = self._get_worksheet_name("custom_schedules")

            # Try to get worksheet, create if doesn't exist
            try:
                sheet = self.spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                sheet = self.spreadsheet.add_worksheet(title=worksheet_name, rows=100, cols=10)

            sheet.clear()
            sheet.update('A1', [[json.dumps(schedule_data)]])
            return True
        except Exception as e:
            st.error(f"Failed to save custom schedule: {e}")
            return False

    def load_custom_schedule(self):
        """Load custom schedule configuration for current season"""
        if not self.spreadsheet:
            return {}

        try:
            worksheet_name = self._get_worksheet_name("custom_schedules")
            sheet = self.spreadsheet.worksheet(worksheet_name)
            data = sheet.get('A1')

            if data and data[0] and data[0][0]:
                return json.loads(data[0][0])
            return {}
        except gspread.WorksheetNotFound:
            # Worksheet doesn't exist yet for this season - this is normal
            return {}
        except Exception as e:
            st.warning(f"Could not load custom schedule: {e}")
            return {}

    def get_available_seasons(self):
        """Get list of seasons that have data"""
        if not self.spreadsheet:
            return []

        try:
            worksheets = self.spreadsheet.worksheets()
            seasons = set()

            for ws in worksheets:
                # Look for worksheets with pattern: playoff_matchups_YYYY or custom_schedules_YYYY
                if ws.title.startswith('playoff_matchups_') or ws.title.startswith('custom_schedules_'):
                    parts = ws.title.split('_')
                    if len(parts) >= 3 and parts[-1].isdigit():
                        seasons.add(int(parts[-1]))

            return sorted(list(seasons), reverse=True)  # Most recent first
        except Exception as e:
            st.warning(f"Could not get available seasons: {e}")
            return []


# Initialize storage singleton
@st.cache_resource
def get_storage(season=None):
    """Get or create the storage instance for a specific season"""
    return LeagueStorage(season)
