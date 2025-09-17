import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from models import MDFInfo, ChannelInfo, ChannelData

try:
    from asammdf import MDF  # type: ignore
    HAS_ASAMMDF = True
except ImportError:
    HAS_ASAMMDF = False
    MDF = None  # type: ignore
    print("Warning: asammdf not installed. Using simulation mode.")

class MDFProcessor:
    """MDF 파일 처리 클래스"""
    
    def __init__(self):
        self.use_simulation = not HAS_ASAMMDF
        
    def process_file(self, file_path: str) -> MDFInfo:
        """MDF 파일 처리 및 기본 정보 추출"""
        if self.use_simulation:
            return self._simulate_file_info(file_path)
        
        try:
            if not HAS_ASAMMDF or MDF is None:
                return self._simulate_file_info(file_path)

            with MDF(file_path) as mdf:
                # 기본 파일 정보
                file_size = os.path.getsize(file_path)
                channel_count = len(mdf.channels_db)
                
                # 메타데이터 추출
                version = str(mdf.version)
                
                # 측정 시작 시간
                measurement_start = None
                if hasattr(mdf.header, 'start_time') and mdf.header.start_time:
                    measurement_start = mdf.header.start_time
                
                # 측정 지속시간 계산
                measurement_duration = None
                if len(mdf.groups) > 0:
                    # 첫 번째 그룹의 시간 정보로부터 duration 계산
                    first_group = mdf.groups[0]
                    if hasattr(first_group, 'channel_group') and first_group.channel_group:
                        # 가장 긴 시간 채널 찾기
                        max_time = 0
                        ch_nr = getattr(first_group.channel_group, 'ch_nr', 0)
                        for ch_index in range(ch_nr):
                            try:
                                signal = mdf.get(group=0, index=ch_index)
                                if signal.timestamps is not None and len(signal.timestamps) > 0:
                                    max_time = max(max_time, signal.timestamps[-1])
                            except:
                                continue
                        measurement_duration = max_time
                
                # 주석 정보
                measurement_comment = ""
                if hasattr(mdf.header, 'comment') and mdf.header.comment:
                    measurement_comment = str(mdf.header.comment)
                
                return MDFInfo(
                    version=version,
                    file_size=file_size,
                    channel_count=channel_count,
                    measurement_start=measurement_start,
                    measurement_duration=measurement_duration,
                    measurement_comment=measurement_comment,
                    vehicle_identification="",
                    recorder_identification=""
                )
                
        except Exception as e:
            print(f"Error processing MDF file: {e}")
            return self._simulate_file_info(file_path)
    
    def get_channels(self, file_path: str) -> List[ChannelInfo]:
        """채널 목록 추출 - 중복 채널명 처리 개선"""
        if self.use_simulation:
            return self._simulate_channels()
        
        try:
            if not HAS_ASAMMDF or MDF is None:
                return self._simulate_channels()

            with MDF(file_path) as mdf:
                channels = []
                processed_channels = set()

                # 모든 그룹을 순회하여 채널 정보 수집
                for group_idx, group in enumerate(mdf.groups):
                    if not hasattr(group, 'channel_group') or not group.channel_group:
                        continue
                    
                    # 그룹 내 모든 채널 처리
                    ch_nr = getattr(group.channel_group, 'ch_nr', 0)
                    for ch_idx in range(ch_nr):
                        try:
                            # 채널명 먼저 확인
                            channel = group.channels[ch_idx]
                            if isinstance(channel.name, bytes):
                                ch_name = channel.name.decode('utf-8')
                            else:
                                ch_name = str(channel.name)
                            
                            # 채널명이 중복되는 경우 그룹 인덱스 추가
                            original_name = ch_name
                            if ch_name in processed_channels:
                                ch_name = f"{original_name}_G{group_idx}"
                            
                            # 여전히 중복이면 채널 인덱스도 추가
                            counter = 1
                            while ch_name in processed_channels:
                                ch_name = f"{original_name}_G{group_idx}_C{counter}"
                                counter += 1
                            
                            processed_channels.add(ch_name)
                            
                            # 신호 데이터 가져오기 (그룹과 인덱스 명시)
                            try:
                                signal = mdf.get(group=group_idx, index=ch_idx)
                            except:
                                # 이름으로 시도 (첫 번째 발생만 가져옴)
                                try:
                                    signal = mdf.get(original_name, group=group_idx, index=ch_idx)
                                except:
                                    signal = mdf.get(original_name)
                            
                            # 채널 기본 정보
                            unit = signal.unit if hasattr(signal, 'unit') else ""
                            description = signal.comment if hasattr(signal, 'comment') else ""
                            sample_count = len(signal.samples) if hasattr(signal, 'samples') and signal.samples is not None else 0
                            
                            # 데이터 타입 결정
                            data_type = "float64"
                            if hasattr(signal, 'samples') and signal.samples is not None:
                                data_type = str(signal.samples.dtype)
                            
                            # 최솟값, 최댓값 계산
                            min_value = None
                            max_value = None
                            if hasattr(signal, 'samples') and signal.samples is not None and len(signal.samples) > 0:
                                try:
                                    min_value = float(np.min(signal.samples))
                                    max_value = float(np.max(signal.samples))
                                except:
                                    pass
                            
                            channel_info = ChannelInfo(
                                name=ch_name,
                                unit=unit,
                                description=description,
                                sample_count=sample_count,
                                data_type=data_type,
                                min_value=min_value,
                                max_value=max_value
                            )
                            channels.append(channel_info)
                            
                        except Exception as e:
                            print(f"Error processing channel in group {group_idx}, index {ch_idx}: {e}")
                            continue
                
                return sorted(channels, key=lambda x: x.name)
                
        except Exception as e:
            print(f"Error getting channels: {e}")
            return self._simulate_channels()
    
    def get_channel_data(self, file_path: str, channel_names: List[str]) -> List[ChannelData]:
        """선택된 채널들의 데이터 추출 - 중복 채널명 처리 개선"""
        if self.use_simulation:
            return self._simulate_channel_data(channel_names)
        
        try:
            if not HAS_ASAMMDF or MDF is None:
                return self._simulate_channel_data(channel_names)

            with MDF(file_path) as mdf:
                channel_data = []
                
                for ch_name in channel_names:
                    try:
                        signal = None
                        
                        # 채널명에 그룹 정보가 포함된 경우 파싱
                        if '_G' in ch_name and ch_name.count('_G') >= 1:
                            # 예: "t_G1" 또는 "t_G1_C2" 형태
                            parts = ch_name.split('_G')
                            original_name = parts[0]
                            
                            if len(parts) > 1:
                                group_part = parts[1]
                                if '_C' in group_part:
                                    # "1_C2" -> group_idx=1, ch_idx=2
                                    group_idx_str, ch_idx_str = group_part.split('_C')
                                    try:
                                        group_idx = int(group_idx_str)
                                        ch_idx = int(ch_idx_str) - 1  # 0-based index
                                        signal = mdf.get(group=group_idx, index=ch_idx)
                                    except:
                                        pass
                                else:
                                    # "1" -> group_idx=1
                                    try:
                                        group_idx = int(group_part)
                                        signal = mdf.get(original_name, group=group_idx)
                                    except:
                                        pass
                        
                        # 기본 방법으로 시도
                        if signal is None:
                            try:
                                # 원본 이름에서 그룹 정보 제거하고 시도
                                clean_name = ch_name.split('_G')[0]
                                signal = mdf.get(clean_name)
                            except:
                                # 전체 이름으로 시도
                                signal = mdf.get(ch_name)
                        
                        if signal is None:
                            raise Exception("Signal not found")
                        
                        # 타임스탬프와 값 추출
                        timestamps = []
                        values = []
                        
                        if hasattr(signal, 'timestamps') and signal.timestamps is not None:
                            timestamps = signal.timestamps.tolist()
                        
                        if hasattr(signal, 'samples') and signal.samples is not None:
                            # numpy array를 파이썬 list로 변환
                            try:
                                values = signal.samples.tolist()
                            except:
                                # 복잡한 데이터 타입의 경우
                                values = [float(x) if np.isfinite(x) else 0.0 for x in signal.samples.flatten()]
                        
                        # 샘플레이트 계산
                        sample_rate = None
                        if len(timestamps) > 1:
                            dt = timestamps[1] - timestamps[0]
                            sample_rate = 1.0 / dt if dt > 0 else None
                        
                        unit = signal.unit if hasattr(signal, 'unit') else ""
                        
                        data = ChannelData(
                            name=ch_name,
                            unit=unit,
                            timestamps=timestamps,
                            values=values,
                            sample_rate=sample_rate
                        )
                        channel_data.append(data)
                        
                    except Exception as e:
                        print(f"Error extracting data for channel {ch_name}: {e}")
                        # 에러 발생 시 빈 데이터로 처리
                        data = ChannelData(
                            name=ch_name,
                            unit="",
                            timestamps=[],
                            values=[],
                            sample_rate=None
                        )
                        channel_data.append(data)
                
                return channel_data
                
        except Exception as e:
            print(f"Error getting channel data: {e}")
            return self._simulate_channel_data(channel_names)
    
    def _simulate_file_info(self, file_path: str) -> MDFInfo:
        """시뮬레이션된 파일 정보"""
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 1024000
        
        return MDFInfo(
            version="4.10",
            file_size=file_size,
            channel_count=200,
            measurement_start=datetime.now(),
            measurement_duration=100.0,
            measurement_comment="Simulated MDF file for testing",
            vehicle_identification="SIM_VEHICLE_001",
            recorder_identification="SIM_RECORDER_001"
        )
    
    def _simulate_channels(self) -> List[ChannelInfo]:
        """시뮬레이션된 채널 목록"""
        prefixes = ['ENGINE_', 'VEHICLE_', 'BRAKE_', 'TRANSMISSION_', 'ECU_', 'SENSOR_']
        suffixes = ['TEMP', 'PRESSURE', 'SPEED', 'VOLTAGE', 'CURRENT', 'POSITION', 'ANGLE', 'TORQUE']
        units = ['°C', 'bar', 'km/h', 'V', 'A', 'mm', '°', 'Nm']
        
        channels = []
        
        for i in range(200):
            prefix = prefixes[i % len(prefixes)]
            suffix = suffixes[i % len(suffixes)]
            unit = units[i % len(units)]
            number = str(i + 1).zfill(3)
            
            channel_name = f"{prefix}{suffix}_{number}"
            
            # 시뮬레이션된 값 범위
            min_val = np.random.uniform(-100, 0)
            max_val = np.random.uniform(min_val + 10, min_val + 200)
            
            channel = ChannelInfo(
                name=channel_name,
                unit=unit,
                description=f"Simulated channel {channel_name}",
                sample_count=1000,
                data_type="float64",
                min_value=min_val,
                max_value=max_val
            )
            channels.append(channel)
        
        return sorted(channels, key=lambda x: x.name)
    
    def _simulate_channel_data(self, channel_names: List[str]) -> List[ChannelData]:
        """시뮬레이션된 채널 데이터"""
        channel_data = []
        
        # 공통 타임스탬프 생성 (0.1초 간격으로 100초)
        time_points = 1000
        time_step = 0.1
        timestamps = [i * time_step for i in range(time_points)]
        
        for ch_name in channel_names:
            # 채널별 시뮬레이션된 데이터 생성
            np.random.seed(hash(ch_name) % 2**32)  # 채널명 기반으로 일관된 시드
            
            frequency = np.random.uniform(0.5, 2.5)  # 0.5-2.5 Hz
            amplitude = np.random.uniform(10, 110)   # 10-110 범위
            offset = np.random.uniform(-25, 25)      # -25~25 오프셋
            
            values = []
            for i, t in enumerate(timestamps):
                # 기본 사인파 + 노이즈
                base_value = amplitude * np.sin(frequency * t * 2 * np.pi) + offset
                noise = np.random.normal(0, amplitude * 0.05)  # 5% 노이즈
                values.append(base_value + noise)
            
            # 단위 결정
            unit_mapping = {
                'TEMP': '°C',
                'PRESSURE': 'bar', 
                'SPEED': 'km/h',
                'VOLTAGE': 'V',
                'CURRENT': 'A',
                'POSITION': 'mm',
                'ANGLE': '°',
                'TORQUE': 'Nm'
            }
            
            unit = ""
            for key, val in unit_mapping.items():
                if key in ch_name:
                    unit = val
                    break
            
            data = ChannelData(
                name=ch_name,
                unit=unit,
                timestamps=timestamps,
                values=values,
                sample_rate=1.0 / time_step
            )
            channel_data.append(data)
        
        return channel_data