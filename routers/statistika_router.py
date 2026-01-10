from fastapi import APIRouter, status, HTTPException
from models.request_model import CallRequest
from services.request_statistics_service import RequestStatisticsService

router = APIRouter(prefix="/statistics", tags=["statistics"])

statistics_service = RequestStatisticsService()


@router.post("/log-call", status_code=status.HTTP_201_CREATED)
async def log_call(request: CallRequest):
    """
    POST - Logs API call from another service
    Request body: { "klicanaStoritev": "/registrirajUporabnika" }
    """
    try:
        statistics_service.save_call(request.klicanaStoritev)
        return {
            "message": "Call logged successfully",
            "endpoint": request.klicanaStoritev,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/last-called-endpoint", status_code=status.HTTP_200_OK)
async def get_last_called_endpoint():
    """
    GET - Returns the last called endpoint
    """
    try:
        result = statistics_service.get_last_called_endpoint()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/most-called-endpoint", status_code=status.HTTP_200_OK)
async def get_most_called_endpoint():
    """
    GET - Returns the most frequently called endpoint
    """
    try:
        result = statistics_service.get_most_called_endpoint()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/all-calls-statistics", status_code=status.HTTP_200_OK)
async def get_all_calls_statistics():
    """
    GET - Returns count of calls for each endpoint
    """
    try:
        result = statistics_service.get_all_calls_statistics()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
