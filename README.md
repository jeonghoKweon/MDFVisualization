# 📊 MDF File Graph Viewer_Jeongho Kwon

**Measurement Data Format (MDF) 파일을 읽고 인터랙티브 그래프로 시각화하는 웹 애플리케이션**

## 🌟 주요 기능

- **실제 MDF 파일 처리**: asammdf 라이브러리를 사용한 정확한 측정 데이터 시각화
- **인터랙티브 웹 인터페이스**: 드래그 앤 드롭으로 간편한 파일 업로드
- **스마트 채널 선택**: 검색, 페이지네이션, 최대 20개 채널 동시 선택
- **다양한 차트 옵션**: 단일 그래프 또는 복수 개별 그래프 표시
- **데이터 내보내기**: 선택된 채널을 CSV 형식으로 내보내기
- **시뮬레이션 모드**: asammdf 없이도 테스트 가능한 데모 모드

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 프로젝트 클론
git clone <repository-url>
cd MDF-Converter

# Python 의존성 설치
cd backend
pip install -r requirements.txt
```

### 2. 백엔드 서버 실행

```bash
# 방법 1: 직접 실행
python main.py

# 방법 2: 헬퍼 스크립트 사용 (의존성 자동 체크)
python start_server.py
```

서버가 실행되면:
- **API 서버**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

### 3. 웹 인터페이스 접속

브라우저에서 프로젝트 루트의 `index.html` 파일을 열어주세요.

## 📁 프로젝트 구조

```
MDF-Converter/
├── 🌐 Frontend Files
│   ├── index.html                   # 메인 웹 인터페이스
│   ├── mdf-viewer-backend.js        # 백엔드 연동 클라이언트
│   ├── mdf-viewer.js               # 독립 시뮬레이션 버전
│   ├── singlechart-popup.html      # 단일 차트 표시 창
│   └── doublechart-popup.html      # 복수 차트 표시 창
├── 🐍 Backend Directory
│   ├── main.py                     # FastAPI 메인 서버
│   ├── mdf_processor.py            # MDF 파일 처리 로직 (✨ 최적화됨)
│   ├── models.py                   # Pydantic 데이터 모델
│   ├── start_server.py             # 서버 시작 헬퍼
│   └── requirements.txt            # Python 의존성 (✨ 향상됨)
├── 📖 Documentation
│   ├── README.md                   # 이 파일
│   └── CLAUDE.md                   # 개발자 가이드
├── ⚙️ Configuration
│   └── .gitignore                  # 버전 관리 규칙 (✨ 새로 추가)
└── 🔧 Environment
    └── venv/                       # Python 가상 환경
```

## 🛠️ 기술 스택

### 백엔드
- **FastAPI**: 고성능 웹 API 프레임워크
- **asammdf**: MDF 파일 처리 전문 라이브러리
- **Pydantic**: 데이터 검증 및 직렬화
- **NumPy**: 수치 계산
- **Uvicorn**: ASGI 서버

### 프론트엔드
- **Vanilla JavaScript**: 순수 자바스크립트
- **Plotly.js**: 인터랙티브 차트 라이브러리
- **HTML5/CSS3**: 모던 웹 표준

## 📋 사용 방법

### 1. 파일 업로드
- MDF 파일(.mdf, .mf4)을 드래그하여 업로드 영역에 놓기
- 또는 "📁 파일 선택" 버튼 클릭하여 파일 선택

### 2. 채널 선택
- 파일 처리 완료 후 채널 목록에서 원하는 채널 선택 (최대 20개)
- 검색 기능을 사용하여 특정 채널 빠르게 찾기
- 페이지네이션을 통해 많은 채널 탐색

### 3. 차트 유형 선택
- **단일 그래프**: 모든 채널을 하나의 차트에 표시
- **복수 그래프**: 각 채널을 개별 차트에 표시

### 4. 그래프 생성 및 내보내기
- "📊 그래프 그리기" 버튼으로 시각화
- "📄 CSV 내보내기" 버튼으로 데이터 다운로드

## 🔧 API 엔드포인트

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| `GET` | `/` | API 상태 확인 |
| `POST` | `/api/upload` | MDF 파일 업로드 |
| `GET` | `/api/channels/{session_id}` | 채널 목록 조회 |
| `POST` | `/api/data/{session_id}` | 채널 데이터 조회 |
| `POST` | `/api/export/csv/{session_id}` | CSV 내보내기 |
| `DELETE` | `/api/session/{session_id}` | 세션 정리 |

## 📦 의존성

### 필수 패키지 (Core Dependencies)
```
fastapi>=0.104.1          # 웹 프레임워크
uvicorn>=0.24.0           # ASGI 서버
python-multipart>=0.0.6   # 파일 업로드
pydantic>=2.5.0           # 데이터 검증
numpy>=1.24.3             # 수치 계산
python-dateutil>=2.8.2    # 날짜 처리
```

### MDF 파일 처리 (Optional)
```
asammdf>=7.3.16           # MDF 파일 처리 (없으면 시뮬레이션 모드)
```

### 프로덕션 배포용 (Production)
```
gunicorn>=21.2.0          # WSGI HTTP 서버
python-dotenv>=1.0.0      # 환경 변수 관리
```

### 개발/테스트용 (Development)
```
pytest>=7.4.3            # 테스트 프레임워크
pytest-asyncio>=0.21.1   # 비동기 테스트 지원
httpx>=0.25.2             # HTTP 클라이언트 (테스트용)
```

## 🔍 트러블슈팅

### 자주 발생하는 문제들

#### 1. 백엔드 서버 연결 실패
```
❌ 증상: "백엔드 서버에 연결할 수 없습니다" 오류
✅ 해결: backend 디렉터리에서 python main.py 실행 확인
```

#### 2. asammdf 라이브러리 없음
```
❌ 증상: "asammdf not installed. Using simulation mode." 메시지
✅ 해결: pip install asammdf 설치 (실제 MDF 파일 처리용)
ℹ️  참고: 시뮬레이션 모드로도 테스트 가능
```

#### 3. 파일 업로드 실패
```
❌ 증상: 파일 업로드 후 "지원되지 않는 파일 형식" 오류
✅ 해결: .mdf 또는 .mf4 확장자 파일인지 확인
```

#### 4. 메모리 부족
```
❌ 증상: 큰 MDF 파일 처리 시 브라우저 멈춤
✅ 해결: 채널 선택 개수를 20개 이하로 제한
```

### 디버깅 팁
- 브라우저 개발자 도구 → Network 탭에서 API 요청 상태 확인
- 백엔드 터미널에서 상세 오류 로그 확인
- http://localhost:8000/docs 에서 API 직접 테스트

## 🔒 보안 고려사항

**현재 구현 (개발용)**:
- CORS 모든 도메인 허용
- 파일 크기 제한 없음
- 메모리 기반 세션 관리

**프로덕션 배포 시 필요한 보안 강화**:
- 특정 도메인만 CORS 허용
- 파일 업로드 크기 제한
- Redis/DB 기반 세션 관리
- HTTPS 적용
- 입력 데이터 검증 강화

## 🧹 프로젝트 관리

### 코드 품질 관리
- **자동 정리**: Python 캐시 파일 (`.pyc`, `__pycache__`) 자동 제외
- **버전 관리**: 포괄적인 `.gitignore` 파일로 불필요한 파일 추적 방지
- **코드 최적화**: JavaScript-style 메서드를 Python 네이티브 메서드로 개선

### 개발 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r backend/requirements.txt
```

### 정리 명령어
```bash
# Python 캐시 파일 정리
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# 임시 파일 정리
rm -f *.tmp *.temp *.backup
```

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 새로운 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

### 코드 기여 가이드라인
- Python 코드는 PEP 8 스타일 가이드를 따르세요
- 새로운 기능에는 적절한 테스트를 추가하세요
- API 변경 시 문서를 업데이트하세요
- 커밋 메시지는 명확하고 설명적으로 작성하세요

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 👨‍💻 개발자

**Jeongho Kwon**

---

**💡 Tip**: 실제 MDF 파일이 없다면 시뮬레이션 모드로 테스트할 수 있습니다. asammdf 설치 없이도 200개의 가상 채널로 기능을 체험해보세요!