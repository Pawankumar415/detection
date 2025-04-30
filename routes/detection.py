from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form,Query
from fastapi.responses import JSONResponse
from typing import List
import os
import time
from database import get_db
from models.models import Inventory
from services.analysis_services import process_image, process_image_data_add, process_video, process_maintenance_check
import uuid
from sqlalchemy.orm import Session
import asyncio
from concurrent.futures import ThreadPoolExecutor
from services import get_task



router = APIRouter()

UPLOAD_DIR_IMG = "static/uploads/images"
UPLOAD_DIR_VID = "static/uploads/videos"
os.makedirs(UPLOAD_DIR_IMG, exist_ok=True)
os.makedirs(UPLOAD_DIR_VID, exist_ok=True)

router = APIRouter()

UPLOAD_DIR_IMG = "static/uploads/images"



@router.post("/images")
async def analyze_images(
    task_id: int = Form(...),
    token: str = Form(...), 
    media_files: List[UploadFile] = File(...), 
    env: get_task.Environment = Query(get_task.Environment.DEV),
    db: Session = Depends(get_db),
    
):
    try:
        start_time = time.time()
        file_paths = []

        
        for media_file in media_files:
            unique_filename = f"detection_image_{uuid.uuid4()}_{media_file.filename}"
            file_path = os.path.join(UPLOAD_DIR_IMG, unique_filename)

            with open(file_path, "wb") as f:
                f.write(await media_file.read())

            file_paths.append(file_path)

        if not file_paths:
            raise HTTPException(status_code=400, detail="No files were uploaded")

      
        loop = asyncio.get_running_loop()
        results = []

        with ThreadPoolExecutor(max_workers=min(4, os.cpu_count())) as executor:
            inference_tasks = [
                loop.run_in_executor(
                    executor,
                    process_image,
                    file_path,
                    "image",
                    task_id, 
                    token,
                    env,
                    
                  
                )
                for file_path in file_paths
            ]
            inference_results = await asyncio.gather(*inference_tasks)

        results.extend(inference_results)  # Store results

        end_time = time.time()
        #print("Execution time:", end_time - start_time)

        return {"results": results}

    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})
    



@router.post("/video")
async def analyze_video(task_id: int=Form(...),
                        token:str=Form(...),
                        media_file: UploadFile = File(...), 
                        db: Session = Depends(get_db),
                        env: get_task.Environment = Query(get_task.Environment.DEV)):
    try:
        unique_filename = f"detection_video_{media_file.filename}_{uuid.uuid4()}.mp4"
        file_path = os.path.join(UPLOAD_DIR_VID, unique_filename)
        with open(file_path, "wb") as f:
            f.write(await media_file.read())

        result = process_video(file_path=file_path, media_type="video", task_id=task_id, db=db,env=env)

        return JSONResponse(content={"result": result})
    except Exception as e:
        db.rollback()
        return JSONResponse(content={"error": str(e)}, status_code=500)
