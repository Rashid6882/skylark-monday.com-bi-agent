import requests
import json

class MondayClient:
    def __init__(self, api_token: str = None):
        self.api_token = api_token
        self.headers = {
            "Authorization": self.api_token if self.api_token else "",
            "Content-Type": "application/json",
            "API-Version": "2023-10"
        }
        self.url = "https://api.monday.com/v2"

    def is_configured(self) -> bool:
        return bool(self.api_token)

    def test_connection(self) -> bool:
        if not self.is_configured():
            return False
        
        query = "{ me { name is_guest } }"
        try:
            res = requests.post(self.url, json={"query": query}, headers=self.headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                return "data" in data and "me" in data["data"]
            return False
        except Exception:
            return False

    def fetch_board_items(self, board_id: str) -> list:
        """
        Dynamically fetches all columns and items from a monday.com board.
        Handles GraphQL pagination.
        """
        if not self.is_configured():
            return []

        # Constructing query to retrieve board items and columns
        query = f"""
        query {{
          boards (ids: {board_id}) {{
            name
            columns {{
              id
              title
              type
            }}
            items_page (limit: 100) {{
              cursor
              items {{
                id
                name
                column_values {{
                  id
                  text
                  value
                }}
              }}
            }}
          }}
        }}
        """
        try:
            res = requests.post(self.url, json={"query": query}, headers=self.headers, timeout=15)
            if res.status_code != 200:
                return []
            
            data = res.json()
            boards = data.get("data", {}).get("boards", [])
            if not boards:
                return []
            
            board = boards[0]
            columns = {col["id"]: col["title"] for col in board.get("columns", [])}
            raw_items = board.get("items_page", {}).get("items", [])
            
            processed_items = []
            for item in raw_items:
                row = {"item_id": item["id"], "item_name": item["name"]}
                for val in item.get("column_values", []):
                    col_id = val["id"]
                    col_name = columns.get(col_id, col_id)
                    row[col_name] = val.get("text", "")
                processed_items.append(row)
                
            return processed_items
        except Exception:
            return []
