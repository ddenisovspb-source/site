from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from backend.olap_cube import OlapCube  # ← ИЗМЕНЕНО
import os

app = FastAPI(title="OLAP Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== ПУТЬ К EXCEL =====
current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(current_dir)
EXCEL_PATH = os.path.join(base_dir, 'data', 'olap_fixed.xlsx')

print(f"📁 Ищем файл: {EXCEL_PATH}")
print(f"📁 Существует: {os.path.exists(EXCEL_PATH)}")

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

# ===== РАЗДАЧА FRONTEND =====
frontend_dir = os.path.join(base_dir, 'frontend')
print(f"📁 Путь к frontend: {frontend_dir}")
print(f"📁 Существует: {os.path.exists(frontend_dir)}")

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
    
    @app.get("/ui")
    async def serve_ui():
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "index.html not found"}
    
    @app.get("/ui/{path:path}")
    async def serve_ui_files(path: str):
        file_path = os.path.join(frontend_dir, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return {"error": f"File {path} not found"}
    
    print(f"✅ Frontend доступен по адресу: /ui")
else:
    print(f"❌ Папка frontend НЕ НАЙДЕНА")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
