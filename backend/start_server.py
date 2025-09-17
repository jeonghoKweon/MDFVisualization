#!/usr/bin/env python3
"""
MDF File Viewer Backend Server 시작 스크립트
"""

import sys
import subprocess
import pkg_resources
from pathlib import Path

def check_dependencies():
    """필수 의존성 체크"""
    required_packages = [
        'fastapi>=0.104.0',
        'uvicorn>=0.24.0', 
        'python-multipart>=0.0.6',
        'pydantic>=2.5.0',
        'numpy>=1.24.0'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            pkg_name = package.split('>=')[0].split('==')[0]
            pkg_resources.get_distribution(pkg_name)
            print(f"✅ {pkg_name} 설치됨")
        except pkg_resources.DistributionNotFound:
            missing_packages.append(package)
            print(f"❌ {pkg_name} 누락")
    
    # asammdf는 선택사항이므로 별도 체크
    try:
        pkg_resources.get_distribution('asammdf')
        print("✅ asammdf 설치됨 (실제 MDF 파일 처리 가능)")
    except pkg_resources.DistributionNotFound:
        print("⚠️  asammdf 누락 (시뮬레이션 모드로 동작)")
        print("   실제 MDF 파일 처리를 원하면: pip install asammdf")
    
    return missing_packages

def install_dependencies(missing_packages):
    """누락된 의존성 설치"""
    if not missing_packages:
        return True
    
    print(f"\n누락된 패키지 {len(missing_packages)}개를 설치합니다...")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'
        ] + missing_packages)
        print("✅ 모든 의존성이 설치되었습니다.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 패키지 설치 실패: {e}")
        return False

def start_server():
    """서버 시작"""
    print("\n🚀 MDF File Viewer Backend 서버를 시작합니다...")
    print("📍 서버 주소: http://localhost:8000")
    print("📚 API 문서: http://localhost:8000/docs")
    print("🛑 서버 종료: Ctrl+C\n")
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n✅ 서버가 종료되었습니다.")
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")

def main():
    """메인 함수"""
    print("=" * 50)
    print("🔧 MDF File Viewer Backend Server")
    print("=" * 50)
    
    # 현재 디렉터리가 backend인지 확인
    current_dir = Path.cwd()
    if current_dir.name != 'backend':
        if (current_dir / 'backend').exists():
            print("📂 backend 디렉터리로 이동합니다...")
            import os
            os.chdir('backend')
        else:
            print("❌ backend 디렉터리를 찾을 수 없습니다.")
            print("   backend/ 디렉터리에서 실행하거나 프로젝트 루트에서 실행하세요.")
            return
    
    # 의존성 체크
    print("\n🔍 의존성을 확인합니다...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        response = input(f"\n❓ 누락된 패키지를 설치하시겠습니까? (y/n): ")
        if response.lower() in ['y', 'yes']:
            if not install_dependencies(missing_packages):
                return
        else:
            print("❌ 필수 의존성이 없으면 서버를 시작할 수 없습니다.")
            return
    
    # 서버 시작
    start_server()

if __name__ == "__main__":
    main()