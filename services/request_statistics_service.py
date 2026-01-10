from datetime import datetime
from db.firestore import get_db
from models.request_model import CallRequest


class RequestStatisticsService:
    def __init__(self):
        self.db = get_db()
        self.collection_name = "reports"
        self._fix_missing_endpoints()

    def _fix_missing_endpoints(self):
        """Rekonstruiraj endpoint polje v starim dokumentih"""
        try:
            documents = self.db.collection(self.collection_name).stream()
            for doc in documents:
                data = doc.to_dict()
                if "endpoint" not in data:
                    # Rekonstruiraj endpoint iz imena dokumenta
                    doc_name = doc.id
                    # soa-expenseService-expenses -> /expenses
                    endpoint = "/" + doc_name.replace("soa-expenseService-", "").replace("_", "/")
                    doc.reference.update({"endpoint": endpoint})
        except Exception as e:
            print(f"Error fixing endpoints: {e}")

    def save_call(self, called_service: str) -> str:
        # Extract endpoint without user ID
        # Pattern: /{userID}/{resource}/{action}
        # We want only: /{resource}/{action}
        parts = called_service.split("/")

        # Remove empty strings and user ID (first UUID-like part)
        meaningful_parts = [p for p in parts if p and not self._is_uuid(p)]
        endpoint_clean = "/" + "/".join(meaningful_parts) if meaningful_parts else "/"

        endpoint_name = endpoint_clean.lstrip("/").replace("/", "_")
        document_name = f"soa-expenseService-{endpoint_name}"

        doc_ref = self.db.collection(self.collection_name).document(document_name)

        doc = doc_ref.get()

        if doc.exists:
            # Increment the count and update last call time
            current_count = doc.get("count") or 0
            doc_ref.update(
                {
                    "count": current_count + 1,
                    "last_call": datetime.now(),
                }
            )
        else:
            # Create new document with count 1
            doc_ref.set(
                {
                    "endpoint": endpoint_clean,
                    "count": 1,
                    "last_call": datetime.now(),
                }
            )

        return document_name

    def _is_uuid(self, value: str) -> bool:
        """Check if string looks like UUID"""
        if len(value) != 36:
            return False
        parts = value.split("-")
        return len(parts) == 5 and all(len(p) in [8, 4, 4, 4, 12] for p in parts)

    def get_last_called_endpoint(self) -> dict:
        """Returns the last called endpoint"""
        documents = self.db.collection(self.collection_name).stream()

        last_endpoint = None
        last_time = None

        for doc in documents:
            data = doc.to_dict()
            time = data.get("last_call")

            if time and (last_time is None or time > last_time):
                last_time = time
                last_endpoint = data.get("endpoint")

        if last_endpoint:
            return {
                "endpoint": last_endpoint,
                "time": last_time.strftime("%Y/%m/%d %H:%M:%S") if last_time else None,
            }
        return {"error": "No data"}

    def get_most_called_endpoint(self) -> dict:
        """Returns the most frequently called endpoint"""
        documents = self.db.collection(self.collection_name).stream()

        most_called = None
        max_calls = 0

        for doc in documents:
            data = doc.to_dict()
            call_count = data.get("count", 0)

            if call_count > max_calls:
                max_calls = call_count
                most_called = data.get("endpoint")

        if most_called:
            return {"endpoint": most_called, "call_count": max_calls}
        return {"error": "No data"}

    def get_all_calls_statistics(self) -> list:
        """Returns statistics for all calls"""
        documents = self.db.collection(self.collection_name).stream()

        statistics = []

        for doc in documents:
            data = doc.to_dict()
            statistics.append(
                {
                    "endpoint": data.get("endpoint"),
                    "call_count": data.get("count", 0),
                }
            )

        # Sort by call count in descending order
        statistics.sort(key=lambda x: x["call_count"], reverse=True)

        return statistics if statistics else [{"error": "No data"}]
