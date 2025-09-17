from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class ChannelInfo(BaseModel):
    """채널 정보 모델"""
    name: str
    unit: str
    description: Optional[str] = ""
    sample_count: int
    data_type: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    conversion_rule: Optional[str] = None

class ChannelData(BaseModel):
    """채널 데이터 모델"""
    name: str
    unit: str
    timestamps: List[float]
    values: List[Union[float, int]]
    sample_rate: Optional[float] = None
    
    class Config:
        json_encoders = {
            float: lambda v: round(v, 6) if v is not None else None
        }

class MDFInfo(BaseModel):
    """MDF 파일 기본 정보 모델"""
    version: str
    file_size: int
    channel_count: int
    measurement_start: Optional[datetime] = None
    measurement_duration: Optional[float] = None
    measurement_comment: Optional[str] = ""
    vehicle_identification: Optional[str] = ""
    recorder_identification: Optional[str] = ""
    
class UploadResponse(BaseModel):
    """파일 업로드 응답 모델"""
    session_id: str
    filename: str
    file_info: MDFInfo
    message: str

class ChannelsResponse(BaseModel):
    """채널 목록 응답 모델"""
    session_id: str
    channels: List[ChannelInfo]
    total_channels: int

class DataResponse(BaseModel):
    """채널 데이터 응답 모델"""
    session_id: str
    data: List[ChannelData]
    channels_count: int

class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str
    detail: Optional[str] = None
    status_code: int