from datetime import date, datetime
from typing import Optional
from db.firestore import get_db
from models.expense_model import ExpenseResponse
from models.item_model import Item
from models.report_model import Report
from services.expense_service import ExpenseService


class ReportService:
    def __init__(self):
        self.db = get_db()
        self.expense_service = ExpenseService()

    def create_report(
        self, user_id: Optional[str], date_from: Optional[date], date_to: Optional[date]
    ) -> str:
        if user_id is None:
            raise ValueError("User ID is required")

        doc_ref = (
            self.db.collection(user_id)
            .document("reports")
            .collection("reports")
            .document()
        )

        expenses: list[ExpenseResponse] = (
            self.expense_service.get_expenses_in_date_range(user_id, date_from, date_to)
        )

        total_expenses_price = 0
        most_expensive_items: list[Item] = []
        max_price = 0

        if len(expenses) == 0:
            raise ValueError("No expenses found")

        for expense in expenses:
            total_expenses_price += expense.total_price

            for item in expense.items:
                if item.item_price >= max_price:
                    max_price = item.item_price

        for expense in expenses:
            for item in expense.items:
                if item.item_price >= max_price:
                    most_expensive_items.append(item)

        if date_to is None:
            date_to = date.today()

        report = Report(
            date_from=date_from,
            date_to=date_to,
            expenses=expenses,
            most_expensive_items=most_expensive_items,
            total_price=total_expenses_price,
            created_at=datetime.now(),
        )

        report_dict = report.model_dump()
        if report_dict.get("date_from"):
            report_dict["date_from"] = datetime.combine(
                report_dict["date_from"], datetime.min.time()
            )
        if report_dict.get("date_to"):
            report_dict["date_to"] = datetime.combine(
                report_dict["date_to"], datetime.min.time()
            )

        doc_ref.set(report_dict)
        return doc_ref.id

    def get_all_report_ids(self, user_id: Optional[str]) -> list[str]:
        if user_id is None:
            raise ValueError("User ID is required")

        query = self.db.collection(user_id).document("reports").collection("reports")

        reports: list[str] = []
        query = query.stream()

        for report in query:
            # reports.append(report.to_dict())
            reports.append(report.id)

        return reports

    def get_report_by_id(self, user_id: str, report_id: str):
        query = (
            self.db.collection(user_id)
            .document("reports")
            .collection("reports")
            .document(report_id)
        )

        doc_ref = query.get()
        report = doc_ref.to_dict()

        if report is None:
            raise ValueError("Report not found, check if report id is correct")

        report = Report(
            date_from=report["date_from"],
            date_to=report["date_to"],
            expenses=report["expenses"],
            most_expensive_items=report["most_expensive_items"],
            total_price=report["total_price"],
            created_at=report["created_at"],
        )

        return report

    def delete_report_by_id(self, user_id: str, report_id: str):
        query = (
            self.db.collection(user_id)
            .document("reports")
            .collection("reports")
            .document(report_id)
        )

        if query.get() is None:
            raise ValueError(
                "Report not found, check if report id is correct and user id is correct"
            )

        query.delete()
        return {"message": "Report deleted successfully"}

    def delete_all(self, user_id: str):
        query = self.db.collection(user_id).document("reports").collection("reports")

        docs = query.stream()
        for doc in docs:
            doc.reference.delete()

        return {"message": "All reports deleted successfully"}
