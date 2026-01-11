# AI 글쓰기 자동화봇

네이버 블로그에 자동으로 글을 작성해주는 GUI 프로그램입니다.

## 📋 주요 기능

- ✅ 네이버 블로그 자동 로그인
- ✅ Gemini AI로 블로그 글 자동 생성
- ✅ 키워드 기반 콘텐츠 생성
- ✅ 서식 적용 (굵게, 문단 구분 등)
- ✅ 세련된 GUI 인터페이스
- ✅ 실시간 실행 로그 확인
- ✅ 설정 자동 저장/불러오기

## 🖥️ 설치 방법

### 1. Python 설치
- Python 3.8 이상 버전을 설치하세요
- 다운로드: https://www.python.org/downloads/

### 2. Chrome 브라우저 설치
- Google Chrome 최신 버전을 설치하세요
- 다운로드: https://www.google.com/chrome/

### 3. 프로그램 파일 다운로드
다음 파일들이 모두 같은 폴더에 있어야 합니다:
```
📁 프로젝트 폴더/
  ├── AI글쓰기자동화봇_GUI.py (메인 프로그램)
  ├── gemini.py (Gemini API 모듈)
  ├── requirements.txt (필수 라이브러리 목록)
  └── README.md (이 파일)
```

### 4. 필수 라이브러리 설치

#### Windows (PowerShell 또는 CMD)
```bash
cd "프로젝트 폴더 경로"
pip install -r requirements.txt
```

#### 개별 설치 방법 (위 명령어가 안 될 경우)
```bash
pip install selenium==4.15.2
pip install pyperclip==1.8.2
pip install google-genai==0.2.2
pip install openpyxl==3.1.2
```

## 🚀 실행 방법

### 1. 프로그램 실행
```bash
python AI글쓰기자동화봇_GUI.py
```

### 2. 사용 순서
1. **네이버 로그인 정보 입력**
   - 아이디와 비밀번호 입력

2. **Gemini API 키 설정**
   - API 키 입력
   - "API 키 설정" 버튼 클릭

3. **키워드 입력**
   - 블로그 글 주제 키워드 입력
   - 또는 "핵심 키워드 업로드" 버튼으로 파일 업로드

4. **발행 유형 선택**
   - 즉시 작성: 임시저장
   - 즉시 발행: 바로 발행
   - 예약 발행: 예약 시간 설정

5. **시작 버튼 클릭**
   - 자동화 실행
   - 실행 로그에서 진행 상황 확인

6. **작업 완료 후**
   - 브라우저에서 내용 확인
   - "종지" 버튼으로 브라우저 종료

## 🔑 Gemini API 키 발급

1. Google AI Studio 접속: https://aistudio.google.com/
2. 로그인 후 "Get API Key" 클릭
3. API 키 복사
4. 프로그램에 입력

## ⚙️ 설정 저장

"다음 실행 시 자동으로 로그인 정보 불러오기" 체크 시:
- 네이버 ID/PW
- Gemini API 키
- 위 정보가 `config.json` 파일에 저장됩니다

## 📝 주의사항

1. **네이버 보안**
   - 2단계 인증 설정 시 해제하거나 앱 비밀번호 사용
   - 로그인이 자주 실패할 경우 수동 로그인 후 재시도

2. **Chrome 드라이버**
   - Selenium 4.x 버전은 자동으로 드라이버 설치
   - 별도 설치 불필요

3. **API 사용량**
   - Gemini API 무료 할당량 확인
   - 과도한 사용 시 요금 발생 가능

4. **방화벽/보안 프로그램**
   - 크롬 자동화가 차단될 수 있음
   - 필요 시 예외 처리

## 🐛 문제 해결

### 프로그램이 실행되지 않을 때
```bash
# Python 버전 확인 (3.8 이상이어야 함)
python --version

# 라이브러리 재설치
pip install --upgrade -r requirements.txt
```

### Chrome 드라이버 오류
```bash
# Selenium 업데이트
pip install --upgrade selenium
```

### 모듈을 찾을 수 없다는 오류
```bash
# 현재 폴더에 gemini.py 파일이 있는지 확인
# 없다면 원본 폴더에서 복사
```

### 한글이 깨질 때 (Windows)
- 터미널/CMD를 관리자 권한으로 실행
- 또는 코드 페이지 변경: `chcp 65001`

## 📂 파일 구조

```
프로젝트 폴더/
├── AI글쓰기자동화봇_GUI.py    # 메인 프로그램
├── gemini.py                   # Gemini API 모듈
├── requirements.txt            # 필수 라이브러리
├── README.md                   # 사용 설명서
├── config.json                 # 설정 파일 (자동 생성)
└── 실행로그_*.txt              # 실행 로그 (자동 생성)
```

## 💡 팁

1. **키워드 파일 사용**
   - 여러 키워드를 txt 파일로 저장
   - "핵심 키워드 업로드" 버튼으로 불러오기

2. **설정 저장**
   - 체크박스를 켜두면 다음에 편리

3. **브라우저 유지**
   - 작업 완료 후 브라우저가 유지됨
   - 내용 확인 후 "종지" 버튼 클릭

## 📞 지원

문제가 발생하면:
1. 실행 로그 확인
2. requirements.txt의 라이브러리 버전 확인
3. Python 버전 확인 (3.8 이상)

## 📄 라이선스

개인 사용 및 학습 목적으로 자유롭게 사용하세요.

---

**만든 날짜**: 2026-01-12  
**버전**: 1.0.0
