from fastapi import APIRouter, HTTPException
from services.storage import list_intakes, get_intake

router = APIRouter(prefix="/intakes", tags=["intakes"])


@router.get("")
def get_all_intakes():
    return list_intakes()


@router.get("/{irn}")
def get_intake_by_irn(irn: str):
    intake = get_intake(irn)
    if not intake:
        raise HTTPException(status_code=404, detail="Intake not found")
    return intake
