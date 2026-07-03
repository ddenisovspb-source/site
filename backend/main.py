from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from olap_cube import OlapCube
import os

app = FastAPI(title="OLAP Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXCEL_PATH = 'data/olap_fixed.xlsx'
cube = OlapCube(EXCEL_PATH)

class QueryRequest(BaseModel):
    projects: List[str]
    columns: List[str]

@app.get("/")
def root():
    return {"status": "OLAP Dashboard API is running"}

@app.get("/projects")
def get_projects():
    return {"projects": cube.get_projects()}

@app.get("/columns")
def get_columns():
    return {"columns": cube.get_columns()}

@app.post("/query")
def query_data(request: QueryRequest):
    try:
        data = cube.query(
            projects=request.projects,
            columns=request.columns
        )
        return {
            "data": data,
            "projects": request.projects,
            "columns": request.columns,
            "total_rows": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
