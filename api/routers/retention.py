from fastapi import APIRouter

router=APIRouter(prefix="/retention",tags=["Retention"])


@router.get("/summary")

def summary():

    return {

        "status":"success"

    }