from fastapi import APIRouter

router=APIRouter(prefix="/metrics",tags=["Metrics"])


@router.get("/kpis")

def metrics():

    return {

        "kpis":[

            "MRR",

            "Retention",

            "Revenue At Risk",

            "Customer Health"

        ]

    }