// MDF 파일 뷰어 JavaScript - Backend 연동 버전

class MDFViewerBackend {
    constructor() {
        this.mdfData = null;
        this.channels = [];
        this.selectedChannels = new Set();
        this.currentPage = 1;
        this.channelsPerPage = 44; // 2열 × 22행
        this.filteredChannels = [];
        this.sessionId = null;
        this.apiBaseUrl = 'http://localhost:8000/api';
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        const channelSearch = document.getElementById('channelSearch');

        // 파일 선택 이벤트
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // 드래그 앤 드롭 이벤트
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.loadMDFFile(files[0]);
            }
        });

        // 채널 검색 이벤트
        channelSearch.addEventListener('input', (e) => {
            this.filterChannels(e.target.value);
        });

        // 페이지 언로드 시 세션 정리
        window.addEventListener('beforeunload', () => {
            if (this.sessionId) {
                this.cleanupSession();
            }
        });
    }

    async handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            await this.loadMDFFile(file);
        }
    }

    async loadMDFFile(file) {
        try {
            this.showMessage('파일을 서버에 업로드하고 처리중입니다...', 'loading');
            
            // 파일 확장자 체크
            const validExtensions = ['.mdf', '.mf4'];
            const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
            
            if (!validExtensions.includes(fileExtension)) {
                throw new Error('지원되지 않는 파일 형식입니다. .mdf 또는 .mf4 파일을 선택하세요.');
            }

            // 백엔드로 파일 업로드
            const formData = new FormData();
            formData.append('file', file);

            const uploadResponse = await fetch(`${this.apiBaseUrl}/upload`, {
                method: 'POST',
                body: formData
            });

            if (!uploadResponse.ok) {
                const errorData = await uploadResponse.json();
                throw new Error(errorData.detail || '파일 업로드에 실패했습니다.');
            }

            const uploadData = await uploadResponse.json();
            this.sessionId = uploadData.session_id;
            this.currentFile = file;

            // UI 업데이트: 파일 선택 영역 숨기고 파일 정보 표시
            this.showFileInfo(file, uploadData.file_info);
            
            // 채널 목록 로드
            await this.loadChannels();
            
            this.showMessage(`파일 "${file.name}"을 성공적으로 로드했습니다.`, 'success');
            document.getElementById('chartTypeSection').classList.remove('hidden');
            document.getElementById('mainControls').classList.remove('hidden');
            
        } catch (error) {
            this.showMessage(`오류: ${error.message}`, 'error');
            console.error('File loading error:', error);
        }
    }

    async loadChannels() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/channels/${this.sessionId}`);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || '채널 목록 조회에 실패했습니다.');
            }

            const data = await response.json();
            this.channels = data.channels.map(ch => ch.name);
            this.filteredChannels = [...this.channels];
            this.renderChannelList();
            
        } catch (error) {
            this.showMessage(`채널 목록 로드 오류: ${error.message}`, 'error');
            console.error('Channels loading error:', error);
        }
    }

    showFileInfo(file, fileInfo) {
        // 파일 업로드 영역 숨기기
        document.getElementById('uploadSection').classList.add('hidden');
        
        // 파일 정보 영역 표시
        const fileInfoSection = document.getElementById('fileInfoSection');
        fileInfoSection.classList.remove('hidden');
        
        // 파일 정보 업데이트
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('filePath').textContent = file.name; // 브라우저에서는 전체 경로를 얻을 수 없음
        document.getElementById('fileSize').textContent = this.formatFileSize(file.size);
        document.getElementById('channelCount').textContent = fileInfo.channel_count || '-';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    filterChannels(searchTerm) {
        if (!searchTerm.trim()) {
            this.filteredChannels = [...this.channels];
        } else {
            this.filteredChannels = this.channels.filter(channel =>
                channel.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }
        
        this.currentPage = 1;
        this.renderChannelList();
    }

    renderChannelList() {
        const totalPages = Math.ceil(this.filteredChannels.length / this.channelsPerPage);
        const startIdx = (this.currentPage - 1) * this.channelsPerPage;
        const endIdx = Math.min(startIdx + this.channelsPerPage, this.filteredChannels.length);
        const pageChannels = this.filteredChannels.slice(startIdx, endIdx);

        const channelList = document.getElementById('channelList');
        channelList.innerHTML = '';

        pageChannels.forEach(channel => {
            const channelItem = document.createElement('div');
            channelItem.className = 'channel-item';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `channel_${channel}`;
            checkbox.checked = this.selectedChannels.has(channel);
            checkbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    if (this.selectedChannels.size >= 20) {
                        e.target.checked = false;
                        this.showMessage('성능상의 이유로 최대 20개의 채널만 선택할 수 있습니다.', 'error');
                        return;
                    }
                    this.selectedChannels.add(channel);
                } else {
                    this.selectedChannels.delete(channel);
                }
            });

            const label = document.createElement('label');
            label.htmlFor = `channel_${channel}`;
            label.textContent = channel;
            label.title = channel; // 툴팁으로 전체 이름 표시

            channelItem.appendChild(checkbox);
            channelItem.appendChild(label);
            channelList.appendChild(channelItem);
        });

        this.renderPagination(totalPages);
    }

    renderPagination(totalPages) {
        const pagination = document.getElementById('pagination');
        pagination.innerHTML = '';

        if (totalPages <= 1) return;

        const maxPagesToShow = 9;
        const startPage = Math.max(1, this.currentPage - Math.floor(maxPagesToShow / 2));
        const endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

        // 이전 버튼
        const prevButton = document.createElement('button');
        prevButton.className = 'prev-next';
        prevButton.textContent = '‹prev';
        prevButton.disabled = this.currentPage === 1;
        prevButton.onclick = () => this.goToPage(Math.max(1, this.currentPage - 1));
        pagination.appendChild(prevButton);

        // 첫 페이지 (필요한 경우)
        if (startPage > 1) {
            const firstButton = document.createElement('button');
            firstButton.textContent = '1';
            firstButton.onclick = () => this.goToPage(1);
            pagination.appendChild(firstButton);

            if (startPage > 2) {
                const dots = document.createElement('span');
                dots.className = 'dots';
                dots.textContent = '…';
                pagination.appendChild(dots);
            }
        }

        // 페이지 번호들
        for (let i = startPage; i <= endPage; i++) {
            const pageButton = document.createElement(i === this.currentPage ? 'span' : 'button');
            pageButton.textContent = i;
            
            if (i === this.currentPage) {
                pageButton.className = 'current';
            } else {
                pageButton.onclick = () => this.goToPage(i);
            }
            
            pagination.appendChild(pageButton);
        }

        // 마지막 페이지 (필요한 경우)
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const dots = document.createElement('span');
                dots.className = 'dots';
                dots.textContent = '…';
                pagination.appendChild(dots);
            }

            const lastButton = document.createElement('button');
            lastButton.textContent = totalPages;
            lastButton.onclick = () => this.goToPage(totalPages);
            pagination.appendChild(lastButton);
        }

        // 다음 버튼
        const nextButton = document.createElement('button');
        nextButton.className = 'prev-next';
        nextButton.textContent = 'next›';
        nextButton.disabled = this.currentPage === totalPages;
        nextButton.onclick = () => this.goToPage(Math.min(totalPages, this.currentPage + 1));
        pagination.appendChild(nextButton);
    }

    goToPage(pageNumber) {
        this.currentPage = pageNumber;
        this.renderChannelList();
    }

    showMessage(message, type = 'info') {
        const messageArea = document.getElementById('messageArea');
        messageArea.innerHTML = `<div class="${type}-box">${message}</div>`;
        
        if (type !== 'loading' && type !== 'error') {
            setTimeout(() => {
                messageArea.innerHTML = '';
            }, 3000);
        }
    }

    async getChannelDataFromBackend(selectedChannels) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/data/${this.sessionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(selectedChannels)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || '채널 데이터 조회에 실패했습니다.');
            }

            const data = await response.json();
            return data.data; // 채널 데이터 배열 반환
            
        } catch (error) {
            console.error('Error getting channel data:', error);
            throw error;
        }
    }

    async cleanupSession() {
        if (!this.sessionId) return;
        
        try {
            await fetch(`${this.apiBaseUrl}/session/${this.sessionId}`, {
                method: 'DELETE'
            });
        } catch (error) {
            console.error('Session cleanup error:', error);
        }
    }

    openChartPopup(selectedChannels) {
        if (!this.sessionId || !selectedChannels || selectedChannels.length === 0) {
            this.showMessage('세션 ID 또는 선택된 채널이 없습니다.', 'error');
            return;
        }

        // 선택된 차트 유형 가져오기
        const chartTypeRadios = document.querySelectorAll('input[name="chartType"]');
        let chartType = 'single';
        for (const radio of chartTypeRadios) {
            if (radio.checked) {
                chartType = radio.value;
                break;
            }
        }
        // 차트 유형에 따라 팝업 파일 이름 결정
        let popupFileName = '';
        if (chartType === 'single') {
            popupFileName = 'singlechart-popup.html';
        } else { // 'multiple'
            popupFileName = 'doublechart-popup.html';
        }

        // 팝업 창 매개변수 생성
        const params = new URLSearchParams({
            sessionId: this.sessionId,
            channels: JSON.stringify(selectedChannels),
            chartType: chartType
        });

        // 팝업 창 열기
        const popup = window.open(
            `${popupFileName}?${params.toString()}`, // 결정된 파일 이름을 사용
            'MDFChart',
            'width=1200,height=800,scrollbars=yes,resizable=yes,menubar=no,toolbar=no,location=no,status=no'
        );
        
        if (!popup) {
            this.showMessage('팝업 차단기가 활성화되어 있습니다. 팝업을 허용해 주세요.', 'error');
        } else {
            popup.focus();
        }
    }
}

// 새 파일 선택 함수
function selectNewFile() {
    const viewer = window.mdfViewer;
    
    // 기존 세션 정리
    if (viewer.sessionId) {
        viewer.cleanupSession();
    }
    
    // 상태 초기화
    viewer.sessionId = null;
    viewer.currentFile = null;
    viewer.channels = [];
    viewer.selectedChannels.clear();
    viewer.filteredChannels = [];
    viewer.currentPage = 1;
    
    // UI 초기화
    document.getElementById('fileInfoSection').classList.add('hidden');
    document.getElementById('chartTypeSection').classList.add('hidden');
    document.getElementById('uploadSection').classList.remove('hidden');
    document.getElementById('mainControls').classList.add('hidden');
    document.getElementById('messageArea').innerHTML = '';
    
    // 파일 입력 초기화
    document.getElementById('fileInput').value = '';
}

// 차트 업데이트 함수 - 팝업 창으로 표시
function updateChart() {
    const viewer = window.mdfViewer;
    const selectedChannels = Array.from(viewer.selectedChannels);
    
    if (selectedChannels.length === 0) {
        viewer.showMessage('그래프를 그리려면 최소 하나의 채널을 선택하세요.', 'error');
        return;
    }

    if (selectedChannels.length > 20) {
        viewer.showMessage('성능상의 이유로 최대 20개의 채널만 선택할 수 있습니다.', 'error');
        return;
    }

    if (!viewer.sessionId) {
        viewer.showMessage('먼저 MDF 파일을 업로드하세요.', 'error');
        return;
    }

    // 팝업 창으로 차트 열기
    viewer.openChartPopup(selectedChannels);
    viewer.showMessage(`${selectedChannels.length}개 채널의 차트를 새 창에서 생성 중입니다...`, 'success');
}

// 채널 선택 리셋 함수
function resetChannelSelection() {
    const viewer = window.mdfViewer;
    
    // 모든 선택된 채널 초기화
    viewer.selectedChannels.clear();
    
    // 채널 목록 다시 렌더링
    viewer.renderChannelList();
    
    // 메시지 표시
    viewer.showMessage('채널 선택이 초기화되었습니다.', 'info');
}

// CSV 내보내기 함수
async function exportToCSV() {
    const viewer = window.mdfViewer;
    const selectedChannels = Array.from(viewer.selectedChannels);
    
    if (selectedChannels.length === 0) {
        viewer.showMessage('CSV로 내보낼 채널을 최소 하나 선택하세요.', 'error');
        return;
    }

    if (selectedChannels.length > 20) {
        viewer.showMessage('성능상의 이유로 최대 20개의 채널만 내보낼 수 있습니다.', 'error');
        return;
    }

    if (!viewer.sessionId) {
        viewer.showMessage('먼저 MDF 파일을 업로드하세요.', 'error');
        return;
    }

    try {
        viewer.showMessage('CSV 파일을 생성하고 있습니다...', 'loading');
        
        const response = await fetch(`${viewer.apiBaseUrl}/export/csv/${viewer.sessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(selectedChannels)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'CSV 내보내기에 실패했습니다.');
        }

        // 파일 다운로드 처리
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        
        // Content-Disposition 헤더에서 파일명 추출
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'mdf_export.csv';
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename=([^;]+)/);
            if (filenameMatch) {
                filename = filenameMatch[1].replace(/"/g, '');
            }
        }
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        viewer.showMessage(`${selectedChannels.length}개 채널의 데이터가 CSV로 내보내기 완료되었습니다.`, 'success');
        
    } catch (error) {
        viewer.showMessage(`CSV 내보내기 오류: ${error.message}`, 'error');
        console.error('CSV export error:', error);
    }
}

// 전역 인스턴스 생성
window.mdfViewer = new MDFViewerBackend();