from datetime import date
from fastapi import APIRouter, Path, status, Query, HTTPException, Body, Depends
from models.expense_model import ExpenseRequest
from models.item_model import Item
from services.expense_service import ExpenseService
from services.report_service import ReportService
from routers.auth_dependency import verify_jwt_token

router = APIRouter(prefix="/{user_id}/expenses", tags=["expenses"])

expense_service = ExpenseService()
report_service = ReportService()


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense: ExpenseRequest, 
    user_id: str = Path(...),
    current_user: dict = Depends(verify_jwt_token)
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    print(user_id, expense)
    expense_id = expense_service.create_expense(user_id, expense)
    return {"message": "Expense created successfully", "expense_id": expense_id}


@router.get("/", status_code=status.HTTP_200_OK)
async def get_expense(
    user_id: str = Path(...), 
    date_from: date = Query(None), 
    date_to: date = Query(None),
    current_user: dict = Depends(verify_jwt_token)
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    expenses = expense_service.get_expenses_in_date_range(user_id, date_from, date_to)
    return expenses


@router.put("/{expense_id}/item/{item_id}/update", status_code=status.HTTP_200_OK)
async def update_item_by_id(
    user_id: str = Path(...),
    expense_id: str = Path(...),
    item_id: str = Path(...),
    item: Item = Body(...),
    current_user: dict = Depends(verify_jwt_token)
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    try:
        return expense_service.update_item_by_id(user_id, expense_id, item_id, item)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/description/update", status_code=status.HTTP_200_OK)
async def update_expense_description_by_id(
    user_id: str = Path(...),
    expense_id: str = Query(...),
    description: str = Body(..., embed=True),
    current_user: dict = Depends(verify_jwt_token)
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    try:
        return expense_service.update_expense_description_by_id(
            user_id, expense_id, description
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/report/create", status_code=status.HTTP_201_CREATED)
async def create_report(
    user_id: str = Path(...), 
    date_from: date = Query(None), 
    date_to: date = Query(None),
    current_user: dict = Depends(verify_jwt_token)
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    try:
        report_id = report_service.create_report(user_id, date_from, date_to)
        return {"message": "Report successfuly created", "report id": report_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/reports")
async def get_all_report_ids(
    user_id: str = Path(...),
    current_user: dict = Depends(verify_jwt_token)
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    try:
        return report_service.get_all_report_ids(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/report")
async def get_report_by_id(
    user_id: str = Path(...), 
    report_id: str = Query(...),
    current_user: dict = Depends(verify_jwt_token)
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    try:
        return report_service.get_report_by_id(user_id, report_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/report/delete/{report_id}")
async def delete_report_by_id(
    user_id: str = Path(...), 
    report_id: str = Path(...),
    current_user: dict = Depends(verify_jwt_token)
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    try:
        return report_service.delete_report_by_id(user_id, report_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/report/delete-all")
async def delete_all_reports(
    user_id: str = Path(...),
    current_user: dict = Depends(verify_jwt_token)
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    try:
        return report_service.delete_all(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/expense/delete-all", status_code=status.HTTP_200_OK)
async def delete_all_expenses(
    user_id: str = Path(...),
    current_user: dict = Depends(verify_jwt_token)
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    try:
        return expense_service.delete_all(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/expense/delete/{expense_id}", status_code=status.HTTP_200_OK)
async def delete_expense_by_id(
    user_id: str = Path(...), 
    expense_id: str = Path(...),
    current_user: dict = Depends(verify_jwt_token)
):
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    try:
        return expense_service.delete_by_id(user_id, expense_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
