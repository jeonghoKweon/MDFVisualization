# MDF File Viewer Project - Claude Instructions

## Project Overview

**MDF File Viewer**는 Measurement Data Format (MDF) 파일을 읽고 인터랙티브 그래프로 시각화하는 웹 애플리케이션입니다.

## Architecture

### Frontend
- **index.html**: 메인 웹 인터페이스
- **mdf-viewer-backend.js**: 백엔드와 통신하는 JavaScript 클라이언트
- **mdf-viewer.js**: 독립 실행형 시뮬레이션 버전
- **singlechart-popup.html**: 단일 차트 표시 창
- **doublechart-popup.html**: 복수 차트 표시 창

### Backend (Python FastAPI)
- **main.py**: FastAPI 서버 메인 애플리케이션
- **mdf_processor.py**: MDF 파일 처리 로직
- **models.py**: Pydantic 데이터 모델
- **start_server.py**: 서버 시작 헬퍼 스크립트
- **requirements.txt**: Python 의존성 목록

## Key Features

### MDF 파일 처리
- asammdf 라이브러리를 사용한 실제 MDF 파일 파싱
- 시뮬레이션 모드 지원 (asammdf 없을 시)
- 중복 채널명 처리 및 그룹 인덱스 추가
- 메타데이터 추출 (버전, 측정시간, 지속시간 등)

### 웹 인터페이스
- 드래그 앤 드롭 파일 업로드
- 채널 선택 및 검색 기능
- 페이지네이션으로 많은 채널 탐색
- 단일/복수 차트 표시 옵션
- CSV 데이터 내보내기

### API Endpoints
- `POST /api/upload`: MDF 파일 업로드
- `GET /api/channels/{session_id}`: 채널 목록 조회
- `POST /api/data/{session_id}`: 선택된 채널 데이터 조회
- `POST /api/export/csv/{session_id}`: CSV 내보내기
- `DELETE /api/session/{session_id}`: 세션 정리

## Development Guidelines

### Code Conventions
- Python: PEP 8 스타일 가이드 준수
- JavaScript: ES6+ 모던 문법 사용
- API: RESTful 설계 패턴
- 에러 처리: 상세한 에러 메시지와 적절한 HTTP 상태 코드

### Data Models
```python
# 주요 데이터 모델
ChannelInfo: 채널 메타데이터
ChannelData: 시계열 데이터 (타임스탬프 + 값)
MDFInfo: 파일 기본 정보
```

### Performance Considerations
- 최대 20개 채널 동시 처리 제한
- 임시 파일 자동 정리 메커니즘
- 메모리 효율적인 데이터 처리
- 6자리 소수점 정밀도로 JSON 압축

## Running the Application

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py  # 또는 python start_server.py
```

### Frontend Access
- 브라우저에서 `index.html` 열기
- 백엔드 서버 주소: http://localhost:8000
- API 문서: http://localhost:8000/docs

### Dependencies

**Core Dependencies:**
- fastapi>=0.104.1
- uvicorn>=0.24.0
- python-multipart>=0.0.6
- pydantic>=2.5.0
- numpy>=1.24.3
- python-dateutil>=2.8.2

**MDF Processing (Optional):**
- asammdf>=7.3.16 (실제 MDF 파일 처리용)

**Production Dependencies:**
- gunicorn>=21.2.0 (WSGI HTTP 서버)
- python-dotenv>=1.0.0 (환경 변수 관리)

**Development Dependencies:**
- pytest>=7.4.3 (테스트 프레임워크)
- pytest-asyncio>=0.21.1 (비동기 테스트)
- httpx>=0.25.2 (HTTP 클라이언트)

## Troubleshooting

### Common Issues
1. **asammdf 없음**: 시뮬레이션 모드로 자동 전환
2. **CORS 에러**: 백엔드 서버가 실행 중인지 확인
3. **파일 업로드 실패**: 파일 형식(.mdf, .mf4) 확인
4. **메모리 부족**: 큰 파일의 경우 채널 수 제한

### Debug Mode
- 브라우저 개발자 도구에서 네트워크 탭 확인
- 백엔드 로그에서 상세 오류 메시지 확인
- API 문서(/docs)에서 직접 테스트 가능

## File Structure
```
MDF-Converter/
├── 🌐 Frontend Files
│   ├── index.html                   # 메인 웹 인터페이스
│   ├── mdf-viewer-backend.js        # 백엔드 연동 JavaScript
│   ├── mdf-viewer.js               # 시뮬레이션 모드 JavaScript
│   ├── singlechart-popup.html      # 단일 차트 표시 창
│   └── doublechart-popup.html      # 복수 차트 표시 창
├── 🐍 Backend Directory
│   ├── main.py                     # FastAPI 메인 서버
│   ├── mdf_processor.py            # MDF 파일 처리 로직 (✨ 최적화됨)
│   ├── models.py                   # Pydantic 데이터 모델
│   ├── start_server.py             # 서버 시작 헬퍼
│   └── requirements.txt            # Python 의존성 (✨ 향상됨)
├── 📖 Documentation
│   ├── README.md                   # 프로젝트 문서
│   └── CLAUDE.md                   # 이 파일 (개발자 가이드)
├── ⚙️ Configuration
│   └── .gitignore                  # 버전 관리 규칙 (✨ 새로 추가)
└── 🔧 Environment
    └── venv/                       # Python 가상 환경
```

## Code Quality & Maintenance

### Cleanup & Optimization (Recent Updates)
- **Python Code Optimization**: JavaScript-style `padStart()` method replaced with Python native `zfill()`
- **Cache Management**: Automatic removal of Python bytecode files (`.pyc`, `__pycache__`)
- **Version Control**: Comprehensive `.gitignore` file to exclude unnecessary files
- **Dependencies Enhancement**: Structured requirements with production, development, and testing packages
- **File Organization**: Removed duplicate documentation and organized project structure

### Best Practices
- **Code Style**: PEP 8 compliance for Python, ES6+ for JavaScript
- **Error Handling**: Comprehensive error messages with appropriate HTTP status codes
- **Performance**: Memory-efficient data processing with 20-channel limit
- **Testing**: pytest framework with async support and HTTP client testing
- **Documentation**: Clear separation between user documentation (README.md) and developer guide (CLAUDE.md)

### Development Workflow
```bash
# Setup development environment
python -m venv venv
source venv/bin/activate  # Linux/Mac or venv\Scripts\activate on Windows
pip install -r backend/requirements.txt

# Clean up development artifacts
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Run tests (when implemented)
pytest backend/tests/

# Run server in development mode
python backend/main.py
```

## Security Notes
- CORS는 현재 모든 도메인 허용 (프로덕션에서 제한 필요)
- 임시 파일은 메모리에서 관리 (프로덕션에서 Redis/DB 권장)
- 파일 업로드 크기 제한 없음 (프로덕션에서 제한 필요)
- 세션 관리는 단순한 딕셔너리 (프로덕션에서 보안 강화 필요)

## Production Deployment Considerations
- Use `gunicorn` for production WSGI server
- Implement environment variable management with `python-dotenv`
- Set up comprehensive logging and monitoring
- Enable HTTPS and proper CORS configuration
- Implement proper session management with Redis or database
- Add file upload size limits and validation