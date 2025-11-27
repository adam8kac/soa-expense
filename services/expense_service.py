from typing import Optional
from db.firestore import get_db
from datetime import date, datetime
from models.expense_model import ExpenseRequest, ExpenseResponse
from models.item_model import Item


class ExpenseService:
    def __init__(self):
        self.db = get_db()

    def create_expense(self, user_id: str, expense: ExpenseRequest) -> str:
        doc_ref = (
            self.db.collection(user_id)
            .document("expenses")
            .collection("expenses")
            .document()
        )
        if expense.description == "":
            raise ValueError("Description can not be empty")

        if len(expense.items) == 0:
            raise ValueError("Items can not be empty")

        for item in expense.items:
            if item.item_name == "":
                raise ValueError("Item name can not be empty")
            if item.item_price <= 0:
                raise ValueError("Item price must be greater than 0")
            if item.item_quantity <= 0:
                item.item_quantity = 1

        total_price = 0
        for item in expense.items:
            total_price += item.item_price * item.item_quantity

        expense = ExpenseResponse(
            description=expense.description,
            items=expense.items,
            total_price=total_price,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        print(date.today())
        doc_ref.set(expense.model_dump())
        return doc_ref.id

    def get_expenses_in_date_range(
        self, user_id: Optional[str], date_from: Optional[date], date_to: Optional[date]
    ) -> list[ExpenseResponse]:
        if user_id is None:
            raise ValueError("User ID is required")

        query = self.db.collection(user_id).document("expenses").collection("expenses")

        if date_from is not None:
            date_from_dt = datetime.combine(date_from, datetime.min.time())
            query = query.where("created_at", ">=", date_from_dt)

        if date_to is not None:
            date_to_dt = datetime.combine(date_to, datetime.max.time())
            query = query.where("created_at", "<=", date_to_dt)

        expenses_docs = query.stream()

        expenses: list[ExpenseResponse] = []
        for exp in expenses_docs:
            expense = ExpenseResponse(
                description=exp.to_dict()["description"],
                items=exp.to_dict()["items"],
                total_price=exp.to_dict()["total_price"],
                created_at=exp.to_dict()["created_at"],
                updated_at=exp.to_dict()["updated_at"],
            )
            expenses.append(expense)

        return expenses

    def update_item_by_id(
        self, user_id: str, expense_id: str, item_id: str, item: Item
    ):
        doc_ref = (
            self.db.collection(user_id)
            .document("expenses")
            .collection("expenses")
            .document(expense_id)
        )

        doc = doc_ref.get()
        if not doc.exists:
            raise ValueError(f"Expense with id {expense_id} not found")

        expense_data = doc.to_dict()

        items = []
        for item_dict in expense_data["items"]:
            if "item_id" not in item_dict:
                import uuid

                item_dict["item_id"] = str(uuid.uuid4())
            item_obj = Item(
                item_id=item_dict["item_id"],
                item_name=item_dict["item_name"],
                item_price=item_dict["item_price"],
                item_quantity=item_dict["item_quantity"],
            )
            items.append(item_obj)

        expense = ExpenseResponse(
            description=expense_data["description"],
            items=items,
            total_price=expense_data["total_price"],
            created_at=expense_data["created_at"],
            updated_at=expense_data["updated_at"],
        )

        item_found = False
        for i, existing_item in enumerate(expense.items):
            if existing_item.item_id == item_id:
                expense.items[i] = Item(
                    item_id=item_id,
                    item_name=item.item_name,
                    item_price=item.item_price,
                    item_quantity=item.item_quantity,
                )
                item_found = True
                break

        if not item_found:
            raise ValueError(f"Item with id {item_id} not found in expense")

        total_price = 0
        for item in expense.items:
            total_price += item.item_price * item.item_quantity

        expense.total_price = total_price
        expense.updated_at = datetime.now()

        doc_ref.set(expense.model_dump())
        return {"message": "Item updated successfully"}

    def update_expense_description_by_id(
        self, user_id: str, expense_id: str, description: str
    ):
        doc_ref = (
            self.db.collection(user_id)
            .document("expenses")
            .collection("expenses")
            .document(expense_id)
        )
        doc_ref.update({"description": description})
        return {"message": "Expense description updated successfully"}

    def delete_all(self, user_id: str) -> dict:
        query = (
            self.db.collection(user_id)
            .document("expenses")
            .collection("expenses")
            .stream()
        )

        for doc in query:
            doc.reference.delete()

        return {"message": "All expenses deleted successfully"}

    def delete_by_id(self, user_id: str, expense_id: str) -> dict:
        query = (
            self.db.collection(user_id)
            .document("expenses")
            .collection("expenses")
            .document(expense_id)
        )

        if query.get() is None:
            raise ValueError(f"Expense with id {expense_id} not found")

        query.delete()
        return {"message": "Expense deleted successfully"}
