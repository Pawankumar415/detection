from fastapi import File, UploadFile, HTTPException,APIRouter,Depends, Form,Query
from fastapi.responses import JSONResponse
from database import get_db
from typing import List
from sqlalchemy.orm import Session
from services.analysis_services import generate_response_video,inspection_image_analysis
from services.prompt_generator import inspection_bedroom_prompt
import json
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
import time
from services import get_task



router = APIRouter()

UPLOAD_DIR_IMG = "static/uploads/inspection/images"
UPLOAD_DIR_VID = "static/uploads/inspection/videos"
os.makedirs(UPLOAD_DIR_IMG, exist_ok=True)
os.makedirs(UPLOAD_DIR_VID, exist_ok=True)
# Function to safely parse JSON
def safe_json_loads(response_text):
    if isinstance(response_text, dict):
        return response_text
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON response")


@router.post("/analyze/image/")
async def analyze_image(
    task_id: int = Form(...),
    token: str = Form(...),
    env: get_task.Environment = Query(get_task.Environment.DEV),
    files: List[UploadFile] = File(...),  
    db: Session = Depends(get_db)
):
    start_time=time.time()
    file_paths = []

    # Save uploaded images
    for file in files:
        unique_filename = f"inspection_image_{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR_IMG, unique_filename)

        with open(file_path, "wb") as out_file:
            out_file.write(await file.read())

        file_paths.append(file_path)

    if not file_paths:
        raise HTTPException(status_code=400, detail="No files were uploaded")

    # Parallel processing using ThreadPoolExecutor
    loop = asyncio.get_running_loop()
    results = []
    
    with ThreadPoolExecutor(max_workers=min(4, os.cpu_count())) as executor:
        inference_tasks = [
            loop.run_in_executor(
                executor,
                inspection_image_analysis,
                file_path,
                inspection_bedroom_prompt,
                "image",
                task_id, 
                token,
                env,
            
               
            )
            for file_path in file_paths
        ]
        inference_results = await asyncio.gather(*inference_tasks)
        end_time=time.time()
        #print("Execution time",end_time-start_time)
    
    for file_path, analysis_result in zip(file_paths, inference_results):
        analysis_result = safe_json_loads(analysis_result)
        if "error" in analysis_result:
           
            return JSONResponse(content={"errors": analysis_result["error"]})

        
        end_time=time.time()
        results.append(analysis_result)
        
        #print("Execution time",end_time-start_time)

    return JSONResponse(content={"results": results})


@router.post("/analyze/video/")
async def analyze_video(
    task_id: int = Form(...),  
    token: str = Form(...),
    env: get_task.Environment = Query(get_task.Environment.DEV),
    files: List[UploadFile] = File(...), 
    db: Session = Depends(get_db)
):
    file_paths = []
    results = []

    for file in files:
        unique_filename = f"inspection_video_{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR_VID, unique_filename)

        # Save the uploaded video
        with open(file_path, "wb") as out_file:
            out_file.write(await file.read())

        file_paths.append(file_path)

    if not file_paths:
        raise HTTPException(status_code=400, detail="No files were uploaded")

   
    for file_path in file_paths:
        analysis_result = generate_response_video(
            file_path, 
            prompt=inspection_bedroom_prompt, 
            media_type="video", 
            task_id=task_id, 
            token=token,
            db=db,
            env=env,
        )

        
        analysis_result = safe_json_loads(analysis_result)
        if not analysis_result:
            return "Couldnt process analysis result"

        results.append(analysis_result)

    if not results:
        raise HTTPException(status_code=500, detail="Failed to analyze videos")

    return JSONResponse(content={"results": results})
