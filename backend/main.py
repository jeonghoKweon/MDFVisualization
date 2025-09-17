from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
import tempfile
import os
from typing import List, Dict, Any
import json
import csv
import io
from mdf_processor import MDFProcessor
from models import ChannelInfo, ChannelData, MDFInfo

app = FastAPI(title="MDF File Viewer API", version="1.0.0")

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인 지정 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MDF 프로세서 인스턴스
mdf_processor = MDFProcessor()

# 임시 파일 저장소 (실제 환경에서는 Redis나 DB 사용 권장)
uploaded_files: Dict[str, str] = {}

@app.get("/")
async def root():
    """API 상태 확인"""
    return {"message": "MDF File Viewer API", "status": "running"}

@app.post("/api/upload")
async def upload_mdf_file(file: UploadFile = File(...)):
    """MDF 파일 업로드 및 기본 정보 추출"""
    try:
        # 파일 확장자 검증
        if not file.filename or not file.filename.lower().endswith(('.mdf', '.mf4')):
            raise HTTPException(
                status_code=400, 
                detail="지원되지 않는 파일 형식입니다. .mdf 또는 .mf4 파일만 지원합니다."
            )
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename or '')[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # MDF 파일 처리
        mdf_info = mdf_processor.process_file(tmp_file_path)
        
        # 파일 정보를 메모리에 저장 (세션 ID 생성)
        session_id = os.path.basename(tmp_file_path)
        uploaded_files[session_id] = tmp_file_path
        
        return {
            "session_id": session_id,
            "filename": file.filename,
            "file_info": mdf_info.dict(),
            "message": f"파일 '{file.filename}'을 성공적으로 처리했습니다."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 처리 중 오류가 발생했습니다: {str(e)}")

@app.get("/api/channels/{session_id}")
async def get_channels(session_id: str):
    """세션 ID로 채널 목록 조회"""
    try:
        if session_id not in uploaded_files:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        file_path = uploaded_files[session_id]
        channels = mdf_processor.get_channels(file_path)
        
        return {
            "session_id": session_id,
            "channels": [channel.dict() for channel in channels],
            "total_channels": len(channels)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채널 정보 조회 중 오류가 발생했습니다: {str(e)}")

@app.post("/api/data/{session_id}")
async def get_channel_data(session_id: str, channel_names: List[str]):
    """선택된 채널들의 데이터 조회"""
    try:
        if session_id not in uploaded_files:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        if len(channel_names) > 20:
            raise HTTPException(
                status_code=400, 
                detail="성능상의 이유로 최대 20개의 채널만 선택할 수 있습니다."
            )
        
        file_path = uploaded_files[session_id]
        channel_data = mdf_processor.get_channel_data(file_path, channel_names)
        
        return {
            "session_id": session_id,
            "data": [data.dict() for data in channel_data],
            "channels_count": len(channel_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채널 데이터 조회 중 오류가 발생했습니다: {str(e)}")

@app.post("/api/export/csv/{session_id}")
async def export_csv(session_id: str, channel_names: List[str]):
    """선택된 채널들의 데이터를 CSV 형식으로 내보내기"""
    try:
        if session_id not in uploaded_files:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        if len(channel_names) > 20:
            raise HTTPException(
                status_code=400, 
                detail="성능상의 이유로 최대 20개의 채널만 내보낼 수 있습니다."
            )
        
        file_path = uploaded_files[session_id]
        channel_data = mdf_processor.get_channel_data(file_path, channel_names)
        
        # CSV 데이터 생성
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 헤더 작성
        headers = ['Time (s)']
        for data in channel_data:
            unit_suffix = f" ({data.unit})" if data.unit else ""
            headers.append(f"{data.name}{unit_suffix}")
        writer.writerow(headers)
        
        # 모든 채널의 최대 데이터 포인트 수 찾기
        max_length = max(len(data.timestamps) for data in channel_data) if channel_data else 0
        
        # 데이터 행 작성
        for i in range(max_length):
            row = []
            
            # 시간 값 (첫 번째 채널의 타임스탬프 사용)
            if i < len(channel_data[0].timestamps):
                row.append(f"{channel_data[0].timestamps[i]:.6f}")
            else:
                row.append("")
            
            # 각 채널의 값
            for data in channel_data:
                if i < len(data.values):
                    row.append(f"{data.values[i]:.6f}")
                else:
                    row.append("")
            
            writer.writerow(row)
        
        # CSV 문자열을 바이트로 변환
        csv_data = output.getvalue()
        output.close()
        
        # 파일명 생성 (세션 ID와 채널 수 포함)
        filename = f"mdf_export_{session_id}_{len(channel_names)}channels.csv"
        
        # StreamingResponse로 CSV 파일 다운로드 제공
        return StreamingResponse(
            io.BytesIO(csv_data.encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV 내보내기 중 오류가 발생했습니다: {str(e)}")

@app.delete("/api/session/{session_id}")
async def cleanup_session(session_id: str):
    """세션 정리 (임시 파일 삭제)"""
    try:
        if session_id in uploaded_files:
            file_path = uploaded_files[session_id]
            if os.path.exists(file_path):
                os.unlink(file_path)
            del uploaded_files[session_id]
            return {"message": "세션이 성공적으로 정리되었습니다."}
        else:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 정리 중 오류가 발생했습니다: {str(e)}")

@app.get("/api/sessions")
async def list_sessions():
    """현재 활성 세션 목록"""
    return {
        "active_sessions": list(uploaded_files.keys()),
        "total_sessions": len(uploaded_files)
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )