# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from datetime import datetime
import threading
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip
import time
import re

# gemini 모듈 임포트
try:
    from gemini import GeminiAPI
except ImportError:
    GeminiAPI = None

# 설정 파일 경로
CONFIG_FILE = "config.json"


class NaverBlogAutomationGUI:
    """네이버 블로그 자동화 GUI 프로그램"""
    
    def __init__(self, root):
        """GUI 초기화"""
        self.root = root
        self.root.title("AI 글쓰기 자동화봇")
        self.root.geometry("850x850")
        self.root.resizable(False, False)
        
        # 변수 초기화
        self.naver_id_var = tk.StringVar()
        self.naver_pw_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.save_config_var = tk.BooleanVar(value=True)
        self.keyword_var = tk.StringVar()
        self.publish_type_var = tk.StringVar(value="draft")  # draft, instant, scheduled
        
        # 드라이버 및 실행 상태
        self.driver = None
        self.is_running = False
        self.gemini = None
        
        # 설정 불러오기
        self.load_config()
        
        # GUI 생성
        self.create_widgets()
        
    def create_widgets(self):
        """GUI 위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = tk.Label(
            main_frame,
            text="AI 글쓰기 자동화봇",
            font=("맑은 고딕", 20, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(
            main_frame,
            text="안녕하세요. AI 글쓰기 자동화봇입니다.\n키워드를 입력하고 발행 유형을 선택하면 자동으로 블로그 글을 작성해드립니다.",
            font=("맑은 고딕", 9),
            fg="#7f8c8d"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # 네이버 로그인 섹션
        self.create_login_section(main_frame)
        
        # Gemini API 섹션
        self.create_api_section(main_frame)
        
        # 설정 저장 체크박스
        self.create_save_config_section(main_frame)
        
        # 키워드 입력 섹션
        self.create_keyword_section(main_frame)
        
        # 발행 유형 섹션
        self.create_publish_section(main_frame)
        
        # 실행 로그 섹션
        self.create_log_section(main_frame)
        
        # 버튼 섹션
        self.create_button_section(main_frame)
        
    def create_login_section(self, parent):
        """네이버 로그인 섹션 생성"""
        # 프레임
        login_frame = tk.LabelFrame(
            parent,
            text="네이버 로그인",
            font=("맑은 고딕", 10, "bold"),
            fg="#34495e",
            padx=15,
            pady=10
        )
        login_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 아이디
        id_frame = ttk.Frame(login_frame)
        id_frame.pack(fill=tk.X, pady=5)
        
        id_label = tk.Label(id_frame, text="아이디:", font=("맑은 고딕", 9), width=10, anchor='w')
        id_label.pack(side=tk.LEFT)
        
        id_entry = ttk.Entry(id_frame, textvariable=self.naver_id_var, font=("맑은 고딕", 9))
        id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 비밀번호
        pw_frame = ttk.Frame(login_frame)
        pw_frame.pack(fill=tk.X, pady=5)
        
        pw_label = tk.Label(pw_frame, text="비밀번호:", font=("맑은 고딕", 9), width=10, anchor='w')
        pw_label.pack(side=tk.LEFT)
        
        pw_entry = ttk.Entry(pw_frame, textvariable=self.naver_pw_var, font=("맑은 고딕", 9), show="*")
        pw_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    def create_api_section(self, parent):
        """Gemini API 섹션 생성"""
        # 프레임
        api_frame = tk.LabelFrame(
            parent,
            text="Gemini API 설정",
            font=("맑은 고딕", 10, "bold"),
            fg="#34495e",
            padx=15,
            pady=10
        )
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        # API 키
        api_key_frame = ttk.Frame(api_frame)
        api_key_frame.pack(fill=tk.X, pady=5)
        
        api_key_label = tk.Label(api_key_frame, text="API 키:", font=("맑은 고딕", 9), width=10, anchor='w')
        api_key_label.pack(side=tk.LEFT)
        
        api_key_entry = ttk.Entry(api_key_frame, textvariable=self.api_key_var, font=("맑은 고딕", 9))
        api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # API 키 설정 버튼
        api_button = tk.Button(
            api_key_frame,
            text="API 키 설정",
            font=("맑은 고딕", 9, "bold"),
            bg="#27ae60",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.set_api_key
        )
        api_button.pack(side=tk.LEFT)
        
    def create_save_config_section(self, parent):
        """설정 저장 섹션 생성"""
        # 프레임
        save_frame = tk.LabelFrame(
            parent,
            text="설정 저장",
            font=("맑은 고딕", 10, "bold"),
            fg="#34495e",
            padx=15,
            pady=10
        )
        save_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 체크박스
        save_check = tk.Checkbutton(
            save_frame,
            text="다음 실행 시 자동으로 로그인 정보 불러오기",
            variable=self.save_config_var,
            font=("맑은 고딕", 9),
            fg="#34495e"
        )
        save_check.pack(anchor='w')
        
    def create_keyword_section(self, parent):
        """키워드 입력 섹션 생성"""
        # 프레임
        keyword_frame = tk.LabelFrame(
            parent,
            text="키워드 입력",
            font=("맑은 고딕", 10, "bold"),
            fg="#34495e",
            padx=15,
            pady=10
        )
        keyword_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 키워드 입력
        keyword_input_frame = ttk.Frame(keyword_frame)
        keyword_input_frame.pack(fill=tk.X, pady=5)
        
        keyword_label = tk.Label(keyword_input_frame, text="키워드:", font=("맑은 고딕", 9), width=10, anchor='w')
        keyword_label.pack(side=tk.LEFT)
        
        keyword_entry = ttk.Entry(keyword_input_frame, textvariable=self.keyword_var, font=("맑은 고딕", 9))
        keyword_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 핵심 키워드 업로드 버튼
        upload_button = tk.Button(
            keyword_frame,
            text="핵심 키워드 업로드",
            font=("맑은 고딕", 9, "bold"),
            bg="#27ae60",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.upload_keywords
        )
        upload_button.pack(fill=tk.X, pady=(5, 0))
        
    def create_publish_section(self, parent):
        """발행 유형 섹션 생성"""
        # 프레임
        publish_frame = tk.LabelFrame(
            parent,
            text="발행 유형",
            font=("맑은 고딕", 10, "bold"),
            fg="#34495e",
            padx=15,
            pady=10
        )
        publish_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 라디오 버튼
        radio_frame = ttk.Frame(publish_frame)
        radio_frame.pack(fill=tk.X, pady=5)
        
        draft_radio = tk.Radiobutton(
            radio_frame,
            text="즉시 작성",
            variable=self.publish_type_var,
            value="draft",
            font=("맑은 고딕", 9),
            fg="#34495e",
            command=self.on_publish_type_change
        )
        draft_radio.pack(side=tk.LEFT, padx=(0, 20))
        
        instant_radio = tk.Radiobutton(
            radio_frame,
            text="즉시 발행",
            variable=self.publish_type_var,
            value="instant",
            font=("맑은 고딕", 9),
            fg="#34495e",
            command=self.on_publish_type_change
        )
        instant_radio.pack(side=tk.LEFT, padx=(0, 20))
        
        scheduled_radio = tk.Radiobutton(
            radio_frame,
            text="예약 발행",
            variable=self.publish_type_var,
            value="scheduled",
            font=("맑은 고딕", 9),
            fg="#34495e",
            command=self.on_publish_type_change
        )
        scheduled_radio.pack(side=tk.LEFT)
        
        # 날짜/시간 선택 (예약 발행용)
        self.datetime_frame = ttk.Frame(publish_frame)
        self.datetime_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 초기값: 현재 날짜/시간
        now = datetime.now()
        default_datetime = now.strftime("%Y-%m-%d 오후 %I:%M")
        
        self.datetime_entry = ttk.Entry(
            self.datetime_frame,
            font=("맑은 고딕", 9),
            width=30
        )
        self.datetime_entry.insert(0, default_datetime)
        self.datetime_entry.pack(side=tk.LEFT)
        
        # 초기 상태: 숨김
        self.datetime_frame.pack_forget()
        
    def create_log_section(self, parent):
        """실행 로그 섹션 생성"""
        # 프레임
        log_frame = tk.LabelFrame(
            parent,
            text="실행 로그",
            font=("맑은 고딕", 10, "bold"),
            fg="#34495e",
            padx=15,
            pady=10
        )
        log_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 로그 텍스트 영역
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("맑은 고딕", 9),
            height=8,
            bg="#f8f9fa",
            fg="#2c3e50",
            relief=tk.FLAT,
            borderwidth=1
        )
        self.log_text.pack(fill=tk.X)
        
    def create_button_section(self, parent):
        """버튼 섹션 생성"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 시작 버튼
        self.start_button = tk.Button(
            button_frame,
            text="시작",
            font=("맑은 고딕", 12, "bold"),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=12,
            cursor="hand2",
            command=self.start_automation
        )
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # 종료 버튼
        self.stop_button = tk.Button(
            button_frame,
            text="종지",
            font=("맑은 고딕", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=12,
            cursor="hand2",
            command=self.stop_automation
        )
        self.stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.stop_button.config(state=tk.DISABLED)
        
    def on_publish_type_change(self):
        """발행 유형 변경 시 호출"""
        if self.publish_type_var.get() == "scheduled":
            self.datetime_frame.pack(fill=tk.X, pady=(10, 0))
        else:
            self.datetime_frame.pack_forget()
            
    def set_api_key(self):
        """API 키 설정"""
        api_key = self.api_key_var.get().strip()
        
        if not api_key:
            messagebox.showwarning("경고", "API 키를 입력해주세요.")
            return
        
        try:
            # Gemini API 초기화 시도
            self.gemini = GeminiAPI(api_key=api_key)
            self.log("✓ Gemini API 키가 성공적으로 설정되었습니다.")
            messagebox.showinfo("성공", "API 키가 성공적으로 설정되었습니다.")
        except Exception as e:
            self.log(f"✗ API 키 설정 실패: {str(e)}")
            messagebox.showerror("오류", f"API 키 설정에 실패했습니다.\n{str(e)}")
            
    def upload_keywords(self):
        """핵심 키워드 파일 업로드"""
        file_path = filedialog.askopenfilename(
            title="키워드 파일 선택",
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    keywords = f.read().strip()
                    self.keyword_var.set(keywords)
                    self.log(f"✓ 키워드 파일 업로드 완료: {os.path.basename(file_path)}")
            except Exception as e:
                self.log(f"✗ 파일 읽기 오류: {str(e)}")
                messagebox.showerror("오류", f"파일을 읽을 수 없습니다.\n{str(e)}")
                
    def log(self, message):
        """로그 출력"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update()
        
    def save_config(self):
        """설정 저장"""
        if not self.save_config_var.get():
            return
        
        config = {
            "naver_id": self.naver_id_var.get(),
            "naver_pw": self.naver_pw_var.get(),
            "api_key": self.api_key_var.get()
        }
        
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"설정 저장 실패: {str(e)}")
            
    def load_config(self):
        """설정 불러오기"""
        if not os.path.exists(CONFIG_FILE):
            return
        
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                
            self.naver_id_var.set(config.get("naver_id", ""))
            self.naver_pw_var.set(config.get("naver_pw", ""))
            self.api_key_var.set(config.get("api_key", ""))
        except Exception as e:
            self.log(f"설정 불러오기 실패: {str(e)}")
            
    def start_automation(self):
        """자동화 시작"""
        # 입력 검증
        if not self.naver_id_var.get().strip():
            messagebox.showwarning("경고", "네이버 아이디를 입력해주세요.")
            return
        
        if not self.naver_pw_var.get().strip():
            messagebox.showwarning("경고", "네이버 비밀번호를 입력해주세요.")
            return
        
        if not self.api_key_var.get().strip():
            messagebox.showwarning("경고", "Gemini API 키를 입력해주세요.")
            return
        
        if not self.keyword_var.get().strip():
            messagebox.showwarning("경고", "키워드를 입력해주세요.")
            return
        
        # 설정 저장
        self.save_config()
        
        # 버튼 상태 변경
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_running = True
        
        # 로그 초기화
        self.log_text.delete(1.0, tk.END)
        self.log("="*50)
        self.log("AI 글쓰기 자동화 시작")
        self.log("="*50)
        
        # 별도 스레드에서 실행
        thread = threading.Thread(target=self.run_automation, daemon=True)
        thread.start()
        
    def stop_automation(self):
        """자동화 중지 및 브라우저 종료"""
        self.is_running = False
        
        # 드라이버 종료
        if self.driver:
            try:
                self.driver.quit()
                self.log("✓ 브라우저 종료 완료")
            except:
                pass
            self.driver = None
        
        # 버튼 상태 변경
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.log("="*50)
        self.log("자동화 종료됨")
        self.log("="*50)
        
    def finish_automation(self, close_browser=False):
        """자동화 완료 처리 (브라우저 선택적 종료)"""
        self.is_running = False
        
        # 브라우저 종료 여부에 따라 처리
        if close_browser and self.driver:
            try:
                self.driver.quit()
                self.log("✓ 브라우저 종료 완료")
            except:
                pass
            self.driver = None
        
        # 버튼 상태 변경
        self.start_button.config(state=tk.NORMAL)
        if self.driver:
            # 브라우저가 유지되면 종지 버튼 활성화
            self.stop_button.config(state=tk.NORMAL)
        else:
            # 브라우저가 없으면 종지 버튼 비활성화
            self.stop_button.config(state=tk.DISABLED)
        
    def run_automation(self):
        """자동화 실행 (메인 로직)"""
        try:
            # 1. Gemini API 초기화
            if not self.gemini:
                self.log("Gemini API 초기화 중...")
                self.gemini = GeminiAPI(api_key=self.api_key_var.get())
            
            # 2. 블로그 글 생성
            keyword = self.keyword_var.get().strip()
            self.log(f"키워드: {keyword}")
            self.log("블로그 글 생성 중...")
            
            blog_content = self.generate_blog_content(keyword)
            
            if not blog_content:
                self.log("✗ 블로그 글 생성 실패")
                self.finish_automation(close_browser=True)
                return
            
            self.log(f"✓ 제목: {blog_content['title']}")
            self.log(f"✓ 본문 길이: {len(blog_content['content'])}자")
            
            # 3. 크롬 드라이버 설정
            self.log("\n크롬 드라이버 설정 중...")
            self.driver = self.setup_driver()
            
            # 4. 네이버 로그인
            self.log("\n네이버 로그인 중...")
            if not self.naver_login():
                self.log("✗ 로그인 실패")
                self.finish_automation(close_browser=True)
                return
            
            # 5. 블로그 글 작성
            self.log("\n블로그 글 작성 중...")
            if not self.write_blog_post(blog_content):
                self.log("✗ 블로그 글 작성 실패")
                self.finish_automation(close_browser=False)
                return
            
            # 6. 완료
            self.log("\n="*50)
            self.log("✓ 모든 작업 완료!")
            self.log("브라우저는 유지됩니다. 확인 후 '종지' 버튼을 눌러주세요.")
            self.log("="*50)
            
            messagebox.showinfo("완료", "블로그 글 작성이 완료되었습니다!\n\n브라우저는 유지됩니다.\n확인 후 '종지' 버튼을 눌러주세요.")
            
        except Exception as e:
            self.log(f"\n✗ 오류 발생: {str(e)}")
            messagebox.showerror("오류", f"자동화 실행 중 오류가 발생했습니다.\n{str(e)}")
            self.finish_automation(close_browser=True)
        
        finally:
            # 작업 완료 후 버튼 상태만 변경 (브라우저는 유지)
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
                
    def setup_driver(self):
        """크롬 드라이버 설정"""
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        
        self.log("✓ 크롬 드라이버 설정 완료")
        return driver
        
    def naver_login(self):
        """네이버 로그인"""
        try:
            self.driver.get("https://nid.naver.com/nidlogin.login")
            time.sleep(2)
            
            # 아이디 입력
            id_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "id"))
            )
            self.input_with_clipboard(id_input, self.naver_id_var.get())
            
            # 비밀번호 입력
            pw_input = self.driver.find_element(By.ID, "pw")
            self.input_with_clipboard(pw_input, self.naver_pw_var.get())
            
            # 로그인 버튼 클릭
            login_button = self.driver.find_element(By.ID, "log.login")
            login_button.click()
            
            time.sleep(3)
            self.log("✓ 네이버 로그인 완료")
            
            # 블로그 글쓰기 페이지로 이동
            self.driver.get("https://blog.naver.com/GoBlogWrite.naver")
            time.sleep(5)
            self.log("✓ 블로그 글쓰기 페이지 접속")
            
            return True
            
        except Exception as e:
            self.log(f"✗ 로그인 오류: {str(e)}")
            return False
            
    def input_with_clipboard(self, element, text):
        """클립보드를 이용한 텍스트 입력"""
        element.click()
        time.sleep(0.3)
        
        element.send_keys(Keys.CONTROL + 'a')
        time.sleep(0.1)
        element.send_keys(Keys.DELETE)
        time.sleep(0.1)
        
        pyperclip.copy(text)
        time.sleep(0.1)
        element.send_keys(Keys.CONTROL + 'v')
        time.sleep(0.3)
        
    def remove_markdown(self, text):
        """마크다운 문법 제거"""
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        text = re.sub(r'^[\-\*]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        return text
        
    def generate_blog_content(self, topic):
        """블로그 글 생성"""
        try:
            # 더 구조화된 블로그 글을 위한 커스텀 프롬프트
            custom_prompt = f"""
다음 주제로 보기 좋은 블로그 글을 작성해주세요:

주제: {topic}

요구사항:
1. 매력적이고 클릭하고 싶은 제목을 작성할 것
2. 첫 문단은 독자의 관심을 끄는 인트로로 작성 (2-3줄)
3. 본문은 3-5개의 명확한 문단으로 구성
4. 각 문단은 하나의 핵심 아이디어를 다룰 것
5. 실용적인 정보와 구체적인 예시를 포함
6. 마지막 문단은 간단한 결론 또는 행동 촉구
7. 한국어로 작성하고, 친근하고 읽기 쉬운 문체 사용
8. 마크다운 문법(#, **, *, _, 등)을 절대 사용하지 말 것

형식:
제목: [여기에 제목 - 감탄사나 질문형태로 흥미롭게]

[인트로 문단 - 독자의 공감을 이끌어내는 내용]

[본문 문단 1 - 첫 번째 핵심 내용]

[본문 문단 2 - 두 번째 핵심 내용]

[본문 문단 3 - 세 번째 핵심 내용]

[결론 문단 - 요약 또는 행동 촉구]

블로그 글을 작성해주세요:
"""
            
            blog_post = self.gemini.generate_content(custom_prompt)
            
            # 마크다운 제거
            blog_post = self.remove_markdown(blog_post)
            
            # 제목과 본문 분리
            lines = blog_post.strip().split('\n')
            title = ""
            content_lines = []
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                if line_stripped.startswith('제목:'):
                    title = line_stripped.replace('제목:', '').strip()
                    content_lines = lines[i+1:]
                    break
                elif i == 0 and line_stripped:
                    title = line_stripped
                    content_lines = lines[i+1:]
                    break
            
            if not title and lines:
                title = lines[0].strip()
                content_lines = lines[1:]
            
            # 본문 정리
            content_paragraphs = []
            current_paragraph = []
            
            for line in content_lines:
                line_stripped = line.strip()
                if line_stripped:
                    current_paragraph.append(line_stripped)
                else:
                    if current_paragraph:
                        content_paragraphs.append(' '.join(current_paragraph))
                        current_paragraph = []
            
            if current_paragraph:
                content_paragraphs.append(' '.join(current_paragraph))
            
            content = '\n\n'.join(content_paragraphs)
            
            return {
                "title": title,
                "content": content
            }
            
        except Exception as e:
            self.log(f"✗ 블로그 글 생성 오류: {str(e)}")
            return None
            
    def close_popups(self):
        """팝업 닫기"""
        try:
            close_button_selectors = [
                ".se-popup-button-cancel",
                ".se-help-panel-close-button",
                "[class*='popup'] button[class*='close']",
                "button[aria-label*='닫기']",
            ]
            
            for selector in close_button_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in buttons:
                        if btn.is_displayed():
                            self.driver.execute_script("arguments[0].click();", btn)
                            time.sleep(0.3)
                except:
                    continue
            
            try:
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.ESCAPE)
                actions.perform()
                time.sleep(0.3)
            except:
                pass
                
        except:
            pass
    
    def apply_text_formatting(self, text, is_intro=False):
        """텍스트 입력 및 서식 적용"""
        try:
            if is_intro:
                # 인트로: 굵게 처리
                self.log("    → 인트로 (굵게)")
                
                # 굵게 시작
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.CONTROL + 'b')  # 굵게 ON
                actions.perform()
                time.sleep(0.2)
                
                # 텍스트 입력
                actions = ActionChains(self.driver)
                for char in text:
                    actions.send_keys(char)
                    actions.pause(0.008)
                actions.perform()
                time.sleep(0.2)
                
                # 굵게 종료
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.CONTROL + 'b')  # 굵게 OFF
                actions.perform()
                time.sleep(0.1)
                
            else:
                # 일반 문단: 기본 입력
                actions = ActionChains(self.driver)
                for char in text:
                    actions.send_keys(char)
                    actions.pause(0.008)
                actions.perform()
                time.sleep(0.1)
                    
        except Exception as e:
            self.log(f"    → 텍스트 입력 오류: {str(e)}")
            
    def write_blog_post(self, blog_content):
        """블로그 글 작성"""
        try:
            # iframe 전환
            iframe = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#mainFrame"))
            )
            self.driver.switch_to.frame(iframe)
            time.sleep(3)
            
            # 팝업 닫기
            for _ in range(3):
                self.close_popups()
                time.sleep(0.5)
            
            # 팝업 오버레이 제거
            try:
                self.driver.execute_script("""
                    var popups = document.querySelectorAll('[class*="popup"], [class*="modal"], [class*="overlay"]');
                    popups.forEach(function(el) {
                        el.style.display = 'none';
                        el.style.visibility = 'hidden';
                    });
                """)
            except:
                pass
            
            time.sleep(1)
            
            # 제목 입력
            title_text = blog_content["title"]
            self.log(f"제목 입력: {title_text[:50]}...")
            
            try:
                title_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".se-section-documentTitle"))
                )
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", title_element)
                time.sleep(1)
                
                # 클릭 가능할 때까지 대기
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-section-documentTitle"))
                )
                
                # 여러 방법으로 클릭 시도
                try:
                    title_element.click()
                except:
                    try:
                        self.driver.execute_script("arguments[0].click();", title_element)
                    except:
                        pass
                
                time.sleep(0.5)
                
                # 기존 내용 전체 선택 후 삭제
                try:
                    title_element.send_keys(Keys.CONTROL + 'a')
                    time.sleep(0.2)
                    title_element.send_keys(Keys.DELETE)
                    time.sleep(0.2)
                except:
                    pass
                
                # ActionChains로 실제 타이핑 (더 확실함)
                actions = ActionChains(self.driver)
                for char in title_text:
                    actions.send_keys(char)
                    actions.pause(0.02)  # 천천히 타이핑
                actions.perform()
                
                time.sleep(0.5)
                
                self.log("✓ 제목 입력 완료")
                time.sleep(1)
                    
            except Exception as e:
                self.log(f"✗ 제목 입력 오류: {str(e)}")
                # 오류 발생 시 클립보드 방식으로 재시도
                try:
                    self.log("클립보드 방식으로 재시도 중...")
                    pyperclip.copy(title_text)
                    title_element.send_keys(Keys.CONTROL + 'v')
                    time.sleep(0.5)
                    self.log("✓ 제목 입력 완료 (클립보드 방식)")
                except:
                    self.log("✗ 제목 입력 재시도 실패")
            
            # 본문 입력
            content_text = blog_content["content"]
            self.log(f"본문 입력 중... (총 {len(content_text)}자)")
            
            try:
                content_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".se-section-text"))
                )
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", content_element)
                time.sleep(1)
                
                self.driver.execute_script("""
                    var element = arguments[0];
                    element.click();
                    element.focus();
                """, content_element)
                time.sleep(1)
                
                # 본문을 문단별로 입력 (서식 적용)
                paragraphs = [p.strip() for p in content_text.split('\n\n') if p.strip()]
                self.log(f"총 {len(paragraphs)}개 문단 입력 (서식 적용)...")
                
                for i, paragraph in enumerate(paragraphs):
                    # 첫 번째 문단은 인트로로 굵게
                    if i == 0:
                        self.log(f"  문단 {i+1}/{len(paragraphs)}: 인트로 (굵게)")
                        self.apply_text_formatting(paragraph, is_intro=True)
                    else:
                        self.log(f"  문단 {i+1}/{len(paragraphs)}: 본문")
                        self.apply_text_formatting(paragraph, is_intro=False)
                    
                    # 문단 사이 간격 (2줄 띄우기로 시각적 구분)
                    if i < len(paragraphs) - 1:
                        time.sleep(0.2)
                        actions = ActionChains(self.driver)
                        # 문단 사이에 충분한 공간 (Enter 3번)
                        actions.send_keys(Keys.ENTER)
                        actions.send_keys(Keys.ENTER)
                        actions.send_keys(Keys.ENTER)
                        actions.perform()
                        time.sleep(0.2)
                
                self.log("✓ 본문 입력 완료")
                time.sleep(2)
                    
            except Exception as e:
                self.log(f"✗ 본문 입력 오류: {str(e)}")
            
            # 저장 버튼 클릭
            self.log("저장 버튼 검색 중...")
            
            save_button = None
            try:
                iframe_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for btn in iframe_buttons:
                    try:
                        btn_text = btn.text.strip()
                        if "임시저장" in btn_text or "저장" in btn_text or "완료" in btn_text:
                            save_button = btn
                            self.log(f"저장 버튼 발견: '{btn_text}'")
                            break
                    except:
                        continue
            except:
                pass
            
            if save_button:
                try:
                    self.driver.execute_script("arguments[0].click();", save_button)
                    time.sleep(3)
                    self.log("✓ 저장 완료")
                    self.driver.switch_to.default_content()
                    return True
                except Exception as e:
                    self.log(f"✗ 저장 버튼 클릭 실패: {str(e)}")
            
            # iframe 밖에서 찾기
            self.driver.switch_to.default_content()
            time.sleep(3)
            
            try:
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for btn in all_buttons:
                    try:
                        btn_text = btn.text.strip()
                        if btn_text and ("임시저장" in btn_text or "저장" in btn_text):
                            save_button = btn
                            self.log(f"저장 버튼 발견: '{btn_text}'")
                            break
                    except:
                        continue
            except:
                pass
            
            if save_button:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
                    time.sleep(1)
                    self.driver.execute_script("arguments[0].click();", save_button)
                    time.sleep(3)
                    self.log("✓ 저장 완료")
                    return True
                except Exception as e:
                    self.log(f"✗ 저장 버튼 클릭 실패: {str(e)}")
            
            # 저장 버튼을 못 찾은 경우
            self.log("⚠ 자동 저장 버튼을 찾지 못했습니다.")
            self.log("수동으로 저장 버튼을 눌러주세요.")
            
            return True
            
        except Exception as e:
            self.log(f"✗ 블로그 글 작성 오류: {str(e)}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False


def main():
    """메인 실행 함수"""
    root = tk.Tk()
    app = NaverBlogAutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
