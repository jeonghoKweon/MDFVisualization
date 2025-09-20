// MDF 파일 뷰어 JavaScript

class MDFViewer {
    constructor() {
        this.mdfData = null;
        this.channels = [];
        this.selectedChannels = new Set();
        this.currentPage = 1;
        this.channelsPerPage = 44; // 4열 x 11행
        this.filteredChannels = [];
        
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
    }

    async handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            await this.loadMDFFile(file);
        }
    }

    async loadMDFFile(file) {
        try {
            this.showMessage('파일을 로딩중입니다...', 'loading');
            
            // 실제 MDF 파일 처리를 위해서는 서버사이드 처리가 필요합니다.
            // 여기서는 시뮬레이션된 데이터를 사용합니다.
            
            // 파일 확장자 체크
            const validExtensions = ['.mdf', '.mf4', '.csv'];
            const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));

            if (!validExtensions.includes(fileExtension)) {
                throw new Error('지원되지 않는 파일 형식입니다. .mdf, .mf4 또는 .csv 파일을 선택하세요.');
            }

            // MDF 파일 시뮬레이션 (실제로는 서버에서 처리해야 함)
            await this.simulateMDFProcessing(file);
            
            this.showMessage(`파일 "${file.name}"을 성공적으로 로드했습니다.`, 'success');
            document.getElementById('mainControls').classList.remove('hidden');
            
        } catch (error) {
            this.showMessage(`오류: ${error.message}`, 'error');
        }
    }

    async simulateMDFProcessing(file) {
        // 실제 환경에서는 이 부분이 서버 API 호출이 됩니다
        return new Promise((resolve) => {
            setTimeout(() => {
                // 시뮬레이션된 채널 데이터 생성
                this.channels = this.generateSimulatedChannels();
                this.filteredChannels = [...this.channels];
                this.renderChannelList();
                resolve();
            }, 1500);
        });
    }

    generateSimulatedChannels() {
        // 실제 MDF 파일의 채널을 시뮬레이션
        const prefixes = ['ENGINE_', 'VEHICLE_', 'BRAKE_', 'TRANSMISSION_', 'ECU_', 'SENSOR_'];
        const suffixes = ['TEMP', 'PRESSURE', 'SPEED', 'VOLTAGE', 'CURRENT', 'POSITION', 'ANGLE', 'TORQUE'];
        const channels = [];

        for (let i = 0; i < 200; i++) {
            const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
            const suffix = suffixes[Math.floor(Math.random() * suffixes.length)];
            const number = String(i + 1).padStart(3, '0');
            channels.push(`${prefix}${suffix}_${number}`);
        }

        return channels.sort();
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

    generateSimulatedData(channels) {
        const timePoints = 1000; // 1000개의 시간 포인트
        const timeStep = 0.1; // 0.1초 간격
        
        return channels.map(channel => {
            const x = Array.from({length: timePoints}, (_, i) => i * timeStep);
            const y = Array.from({length: timePoints}, (_, i) => {
                // 각 채널별로 다른 시뮬레이션 데이터 생성
                const frequency = Math.random() * 2 + 0.5; // 0.5-2.5 Hz
                const amplitude = Math.random() * 100 + 10; // 10-110 범위
                const offset = Math.random() * 50 - 25; // -25~25 오프셋
                const noise = (Math.random() - 0.5) * 5; // 노이즈
                
                return amplitude * Math.sin(frequency * i * timeStep * 2 * Math.PI) + offset + noise;
            });
            
            return { name: channel, x: x, y: y };
        });
    }
}

// 차트 업데이트 함수
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

    viewer.showMessage('그래프를 생성 중입니다...', 'loading');

    // 시뮬레이션된 데이터 생성
    const data = viewer.generateSimulatedData(selectedChannels);
    
    // Plotly 차트 생성
    const traces = data.map((trace, index) => ({
        x: trace.x,
        y: trace.y,
        name: trace.name,
        type: 'scatter',
        mode: 'lines',
        line: {
            width: 1.5
        }
    }));

    const layout = {
        title: {
            text: 'MDF 데이터 시각화',
            font: { size: 16 }
        },
        xaxis: {
            title: '시간 (초)',
            gridcolor: '#f0f0f0'
        },
        yaxis: {
            title: '값',
            gridcolor: '#f0f0f0'
        },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        margin: { t: 50, r: 50, b: 50, l: 80 },
        legend: {
            orientation: 'v',
            x: 1.02,
            y: 1,
            bgcolor: 'rgba(255,255,255,0.8)',
            bordercolor: '#E2E2E2',
            borderwidth: 1
        },
        hovermode: 'x unified'
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        displaylogo: false
    };

    Plotly.newPlot('chartContainer', traces, layout, config);
    viewer.showMessage(`${selectedChannels.length}개 채널의 그래프를 성공적으로 생성했습니다.`, 'success');
}

// 전역 인스턴스 생성
window.mdfViewer = new MDFViewer();