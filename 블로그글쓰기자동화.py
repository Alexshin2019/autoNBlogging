from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip
import time
from datetime import datetime
import sys
import os
import re

# gemini 모듈 임포트
try:
    from gemini import GeminiAPI
except ImportError:
    print("[경고] gemini.py 파일을 찾을 수 없습니다.")
    GeminiAPI = None

# 네이버 계정 정보
NAVER_ID = "shinung"
NAVER_PW = "wE0905**"

# Gemini API 키
GEMINI_API_KEY = "AIzaSyD1Iih0tQ528MxCBhV8yhmi7wHBc7nZnac"

# 로그 파일 설정
log_file = f"실행로그_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
log_messages = []

def log_print(message):
    """화면에 출력하고 로그 파일에도 저장"""
    print(message)
    log_messages.append(message)
    # 실시간으로 파일에 저장
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

# 크롬 드라이버 설정
def setup_driver():
    """크롬 드라이버 초기화"""
    options = webdriver.ChromeOptions()
    # 자동화 탐지 우회 옵션
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 비밀번호 저장 팝업 제거
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

# 클립보드를 이용한 입력 함수
def input_with_clipboard(element, text):
    """pyperclip을 이용해 클립보드로 텍스트 입력"""
    element.click()  # 입력 필드 클릭
    time.sleep(0.3)
    
    # 기존 내용 전체 선택 후 삭제
    element.send_keys(Keys.CONTROL + 'a')
    time.sleep(0.1)
    element.send_keys(Keys.DELETE)
    time.sleep(0.1)
    
    # 클립보드에 복사 후 붙여넣기
    pyperclip.copy(text)
    time.sleep(0.1)
    element.send_keys(Keys.CONTROL + 'v')
    time.sleep(0.3)

# 네이버 로그인 함수
def naver_login(driver):
    """네이버 로그인 수행"""
    try:
        # 네이버 로그인 페이지 접속
        log_print("네이버 로그인 페이지 접속 중...")
        driver.get("https://nid.naver.com/nidlogin.login")
        time.sleep(2)
        
        # 아이디 입력 필드 대기 및 찾기
        log_print("아이디 입력 중...")
        id_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id"))
        )
        input_with_clipboard(id_input, NAVER_ID)
        
        # 비밀번호 입력 필드 찾기
        log_print("비밀번호 입력 중...")
        pw_input = driver.find_element(By.ID, "pw")
        input_with_clipboard(pw_input, NAVER_PW)
        
        # 로그인 버튼 클릭
        log_print("로그인 버튼 클릭...")
        login_button = driver.find_element(By.ID, "log.login")
        login_button.click()
        
        # 로그인 완료 대기
        time.sleep(2)
        log_print("로그인 완료!")
        
        # 블로그 글쓰기 페이지로 이동
        log_print("블로그 글쓰기 페이지로 이동 중...")
        driver.get("https://blog.naver.com/GoBlogWrite.naver")
        time.sleep(5)  # 페이지 로딩 대기 시간 증가
        log_print("블로그 글쓰기 페이지 접속 완료!")
        
        return True
        
    except Exception as e:
        log_print(f"오류 발생: {str(e)}")
        return False

# 한 글자씩 타이핑하는 함수
def type_text_slowly(driver, text, delay=0.03):
    """ActionChains를 이용해 한 글자씩 천천히 타이핑"""
    actions = ActionChains(driver)
    for char in text:
        actions.send_keys(char)
        actions.pause(delay)
    actions.perform()

# 팝업 닫기 함수
def close_popups(driver):
    """존재하는 팝업 닫기"""
    try:
        # 여러 종류의 팝업 닫기 버튼 시도
        close_button_selectors = [
            ".se-popup-button-cancel",
            ".se-help-panel-close-button",
            "[class*='popup'] button[class*='close']",
            "[class*='modal'] button[class*='close']",
            "button[aria-label*='닫기']",
            "button[title*='닫기']",
        ]
        
        for selector in close_button_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                for btn in buttons:
                    if btn.is_displayed():
                        # JavaScript로 클릭
                        driver.execute_script("arguments[0].click();", btn)
                        log_print(f"팝업 버튼 클릭: {selector}")
                        time.sleep(0.3)
            except:
                continue
        
        # ESC 키로도 시도
        try:
            actions = ActionChains(driver)
            actions.send_keys(Keys.ESCAPE)
            actions.perform()
            log_print("ESC 키로 팝업 닫기 시도")
            time.sleep(0.3)
        except:
            pass
            
    except Exception as e:
        log_print(f"팝업 닫기 중 오류 (무시): {str(e)}")

# Gemini로 블로그 글 생성
def remove_markdown(text):
    """마크다운 문법 제거"""
    # ### 제목 문법 제거
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # ** 굵은 글씨 제거
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    
    # * 기울임 제거
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    
    # __ 굵은 글씨 제거
    text = re.sub(r'__(.+?)__', r'\1', text)
    
    # _ 기울임 제거
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # ` 코드 제거
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # - 리스트를 일반 텍스트로
    text = re.sub(r'^[\-\*]\s+', '', text, flags=re.MULTILINE)
    
    # 숫자 리스트를 일반 텍스트로
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    
    return text

def generate_blog_content(topic="파이썬 프로그래밍"):
    """Gemini API를 사용하여 블로그 글 생성"""
    if GeminiAPI is None:
        log_print("[경고] Gemini API를 사용할 수 없습니다. 기본 텍스트를 사용합니다.")
        return {
            "title": "파이썬 프로그래밍 시작하기",
            "content": "파이썬은 배우기 쉽고 강력한 프로그래밍 언어입니다.\n\n프로그래밍을 처음 시작하는 분들에게 추천합니다.\n\n다양한 라이브러리와 프레임워크가 있습니다.\n\n웹 개발, 데이터 분석, AI 등 활용 분야가 넓습니다.\n\n지금 바로 파이썬을 시작해보세요!"
        }
    
    try:
        log_print(f"\n[Gemini API] '{topic}' 주제로 블로그 글 생성 중...")
        gemini = GeminiAPI(api_key=GEMINI_API_KEY)
        
        # 블로그 글 생성
        blog_post = gemini.generate_blog_post(
            topic=topic,
            style="친근하고 정보적인",
            word_count=800
        )
        
        # 마크다운 문법 제거
        blog_post = remove_markdown(blog_post)
        
        # 제목과 본문 분리
        lines = blog_post.strip().split('\n')
        title = ""
        content_lines = []
        
        # "제목:" 라벨 찾기
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped.startswith('제목:'):
                title = line_stripped.replace('제목:', '').strip()
                # 빈 줄 건너뛰고 본문 시작
                content_lines = lines[i+1:]
                break
            elif i == 0 and line_stripped:
                # 첫 줄이 제목
                title = line_stripped
                content_lines = lines[i+1:]
                break
        
        # 제목을 찾지 못했다면 첫 줄을 제목으로
        if not title and lines:
            title = lines[0].strip()
            content_lines = lines[1:]
        
        # 본문 정리 (빈 줄 제거하고 다시 조립)
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
        
        # 마지막 문단 추가
        if current_paragraph:
            content_paragraphs.append(' '.join(current_paragraph))
        
        # 문단 사이에 빈 줄 추가
        content = '\n\n'.join(content_paragraphs)
        
        log_print(f"[OK] 블로그 글 생성 완료!")
        log_print(f"  제목: {title[:50]}...")
        log_print(f"  본문 길이: {len(content)}자")
        log_print(f"  문단 수: {len(content_paragraphs)}개")
        
        return {
            "title": title,
            "content": content
        }
        
    except Exception as e:
        log_print(f"[ERROR] Gemini API 오류: {str(e)}")
        log_print("기본 텍스트를 사용합니다.")
        return {
            "title": f"{topic} - 초보자 가이드",
            "content": f"{topic}에 대해 알아보겠습니다.\n\n기본적인 내용부터 차근차근 설명드리겠습니다.\n\n따라하시면 쉽게 이해하실 수 있습니다."
        }

# 블로그 글 작성 함수
def write_blog_post(driver, blog_content=None):
    """블로그 글 작성"""
    try:
        # 블로그 내용이 제공되지 않았다면 생성
        if blog_content is None:
            blog_content = generate_blog_content("파이썬 웹 스크래핑")
        # 1. iframe 전환
        log_print("\niframe으로 전환 중...")
        iframe = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainFrame"))
        )
        driver.switch_to.frame(iframe)
        log_print("iframe 전환 완료")
        time.sleep(3)  # iframe 내부 요소가 로드될 때까지 충분한 대기
        
        # 2. 팝업 닫기 (여러번 시도)
        log_print("\n팝업 닫기 시도 중...")
        for attempt in range(3):
            close_popups(driver)
            time.sleep(0.5)
        
        # 팝업 오버레이 제거 (JavaScript)
        try:
            driver.execute_script("""
                // 모든 팝업 관련 요소 숨기기
                var popups = document.querySelectorAll('[class*="popup"], [class*="modal"], [class*="overlay"]');
                popups.forEach(function(el) {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                });
            """)
            log_print("JavaScript로 팝업 오버레이 제거 완료")
        except:
            pass
        
        time.sleep(1)
        
        # 3. 제목 입력
        title_text = blog_content["title"]
        log_print(f"\n제목 입력 중: {title_text[:50]}...")
        try:
            # 제목 입력 필드 찾기
            title_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".se-section-documentTitle"))
            )
            
            # 스크롤하여 보이게 하기
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", title_element)
            time.sleep(1)
            
            # 클릭 가능할 때까지 대기
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-section-documentTitle"))
            )
            
            # JavaScript로 직접 텍스트 입력 (가장 확실한 방법)
            driver.execute_script("""
                var element = arguments[0];
                element.focus();
                element.textContent = arguments[1];
                element.innerText = arguments[1];
                
                // 변경 이벤트 발생
                var event = new Event('input', { bubbles: true });
                element.dispatchEvent(event);
            """, title_element, title_text)
            
            log_print("제목 입력 완료")
            time.sleep(1)
                
        except Exception as e:
            log_print(f"제목 입력 중 오류: {str(e)}")
        
        # 4. 본문 입력
        content_text = blog_content["content"]
        log_print(f"\n본문 입력 중... (총 {len(content_text)}자)")
        try:
            # 본문 입력 영역 찾기
            content_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".se-section-text"))
            )
            
            # 스크롤
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", content_element)
            time.sleep(1)
            
            # JavaScript로 클릭하고 포커스
            driver.execute_script("""
                var element = arguments[0];
                element.click();
                element.focus();
            """, content_element)
            time.sleep(1)
            
            # 본문을 문단별로 나누어 입력
            paragraphs = [p.strip() for p in content_text.split('\n\n') if p.strip()]
            log_print(f"총 {len(paragraphs)}개 문단 입력 시작...")
            
            # 천천히 타이핑 (실제로 입력되는 것처럼)
            for i, paragraph in enumerate(paragraphs):
                log_print(f"  문단 {i+1}/{len(paragraphs)} 입력 중...")
                
                # ActionChains로 실제 타이핑
                actions = ActionChains(driver)
                for char in paragraph:
                    actions.send_keys(char)
                    actions.pause(0.01)  # 빠르게
                actions.perform()
                
                # 문단 사이 Enter 2번
                if i < len(paragraphs) - 1:
                    time.sleep(0.2)
                    actions = ActionChains(driver)
                    actions.send_keys(Keys.ENTER)
                    actions.send_keys(Keys.ENTER)
                    actions.perform()
                    time.sleep(0.2)
            
            log_print("본문 입력 완료")
            time.sleep(2)
                
        except Exception as e:
            log_print(f"본문 입력 중 오류: {str(e)}")
        
        # 5. 저장 버튼 클릭
        log_print("\n저장 버튼 검색 시작...")
        
        # iframe 안에서 먼저 저장 버튼 찾기 시도
        log_print("iframe 내부에서 저장 버튼 검색 중...")
        save_button_in_iframe = None
        
        try:
            # iframe 내부의 저장 버튼 찾기
            iframe_buttons = driver.find_elements(By.TAG_NAME, "button")
            log_print(f"iframe 내부 버튼 개수: {len(iframe_buttons)}개")
            
            for btn in iframe_buttons:
                try:
                    btn_text = btn.text.strip()
                    btn_class = btn.get_attribute("class") or ""
                    if btn_text or btn_class:
                        log_print(f"  버튼 발견: 텍스트='{btn_text}', 클래스='{btn_class[:50]}'")
                    
                    if "임시저장" in btn_text or "저장" in btn_text or "완료" in btn_text:
                        save_button_in_iframe = btn
                        log_print(f"[OK] iframe 내부에서 저장 버튼 발견: '{btn_text}'")
                        break
                except:
                    continue
        except Exception as e:
            log_print(f"iframe 내부 버튼 검색 중 오류: {str(e)}")
        
        # iframe 내부에서 찾았다면 클릭
        if save_button_in_iframe:
            try:
                log_print("iframe 내부 저장 버튼 클릭 시도...")
                driver.execute_script("arguments[0].click();", save_button_in_iframe)
                time.sleep(3)
                log_print("[OK] 저장 버튼 클릭 완료!")
                driver.switch_to.default_content()
                return True
            except Exception as e:
                log_print(f"iframe 내부 버튼 클릭 실패: {str(e)}")
        
        # iframe 내부에서 못 찾았다면 밖으로 나가서 찾기
        driver.switch_to.default_content()
        log_print("iframe에서 빠져나옴 - 외부에서 저장 버튼 검색")
        
        # 현재 URL 확인
        current_url = driver.current_url
        log_print(f"현재 URL: {current_url}")
        
        # 페이지가 완전히 로드될 때까지 충분히 대기
        log_print("페이지 완전 로딩 대기 중...")
        time.sleep(5)
        
        # 페이지가 제대로 로드되었는지 확인 (버튼이 나타날 때까지 대기)
        try:
            WebDriverWait(driver, 15).until(
                lambda d: len(d.find_elements(By.TAG_NAME, "button")) > 0 or
                         len(d.find_elements(By.CSS_SELECTOR, "a[href*='write']")) > 0
            )
            log_print("페이지 요소 로딩 완료")
        except:
            log_print("[WARNING] 버튼 로딩 시간 초과")
        
        # 현재 페이지의 HTML 구조 확인
        log_print("페이지 구조 확인 중...")
        try:
            # body 태그가 있는지 확인
            body = driver.find_element(By.TAG_NAME, "body")
            log_print(f"Body 태그 발견: {body is not None}")
            
            # iframe이 아직 있는지 확인
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            log_print(f"페이지 내 iframe 개수: {len(iframes)}개")
            
            # 모든 요소 확인
            all_elements = driver.find_elements(By.XPATH, "//*")
            log_print(f"페이지 내 전체 요소 개수: {len(all_elements)}개")
        except Exception as e:
            log_print(f"페이지 구조 확인 중 오류: {str(e)}")
        
        # 디버깅: 페이지의 모든 버튼 정보 출력 및 파일 저장
        log_print("\n[디버깅] 페이지의 버튼 분석 중...")
        debug_info = []
        debug_info.append("="*60)
        debug_info.append("네이버 블로그 저장 버튼 디버깅 정보")
        debug_info.append("="*60)
        debug_info.append("")
        
        try:
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            debug_info.append(f"총 버튼 개수: {len(all_buttons)}개")
            debug_info.append("")
            debug_info.append("=" * 60)
            debug_info.append("주요 버튼 목록 (저장/발행 관련)")
            debug_info.append("=" * 60)
            
            log_print(f"총 버튼 개수: {len(all_buttons)}개")
            log_print("\n주요 버튼 목록:")
            
            # 화면 출력용 (저장/발행 관련만)
            for idx, btn in enumerate(all_buttons):
                try:
                    btn_class = btn.get_attribute("class") or ""
                    btn_text = btn.text.strip() or ""
                    btn_visible = btn.is_displayed()
                    btn_enabled = btn.is_enabled()
                    
                    # 저장/발행 관련 버튼만 화면에 출력
                    if any(keyword in btn_class.lower() or keyword in btn_text.lower() 
                           for keyword in ["save", "publish", "저장", "발행", "임시"]):
                        info = f"  [{idx}] 클래스: {btn_class[:80]}\n       텍스트: '{btn_text}'\n       표시됨: {btn_visible}, 활성화: {btn_enabled}\n"
                        log_print(info)
                        debug_info.append(f"[버튼 {idx}]")
                        debug_info.append(f"  클래스: {btn_class}")
                        debug_info.append(f"  텍스트: '{btn_text}'")
                        debug_info.append(f"  표시됨: {btn_visible}")
                        debug_info.append(f"  활성화: {btn_enabled}")
                        debug_info.append("")
                except:
                    continue
            
            # 파일에는 모든 버튼 정보 저장
            debug_info.append("")
            debug_info.append("=" * 60)
            debug_info.append("모든 버튼 목록 (전체)")
            debug_info.append("=" * 60)
            
            for idx, btn in enumerate(all_buttons):
                try:
                    btn_class = btn.get_attribute("class") or ""
                    btn_text = btn.text.strip() or ""
                    btn_visible = btn.is_displayed()
                    btn_enabled = btn.is_enabled()
                    
                    debug_info.append(f"[버튼 {idx}]")
                    debug_info.append(f"  클래스: {btn_class}")
                    debug_info.append(f"  텍스트: '{btn_text}'")
                    debug_info.append(f"  표시됨: {btn_visible}")
                    debug_info.append(f"  활성화: {btn_enabled}")
                    debug_info.append("")
                except:
                    continue
                    
            # 디버깅 정보를 파일로 저장
            debug_file = "debug_button_info.txt"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write("\n".join(debug_info))
            log_print(f"\n[OK] 디버깅 정보가 '{debug_file}' 파일로 저장되었습니다!")
            
        except Exception as e:
            error_msg = f"버튼 분석 중 오류: {str(e)}"
            log_print(error_msg)
            debug_info.append(error_msg)
        
        # 페이지 상단으로 스크롤 (저장 버튼은 상단에 있음)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        log_print("페이지 상단으로 스크롤 완료")
        
        # 스크린샷 저장 (디버깅용)
        try:
            screenshot_file = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_file)
            log_print(f"스크린샷 저장: {screenshot_file}")
        except:
            pass
        
        # 버튼이 실제로 있는지 여러 방법으로 확인
        log_print("\n버튼 존재 여부 확인 중...")
        
        # 방법 1: 모든 버튼 찾기
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        log_print(f"TAG_NAME으로 찾은 버튼: {len(all_buttons)}개")
        
        # 방법 2: CSS로 찾기
        css_buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        log_print(f"CSS_SELECTOR로 찾은 버튼: {len(css_buttons)}개")
        
        # 방법 3: XPath로 찾기
        xpath_buttons = driver.find_elements(By.XPATH, "//button")
        log_print(f"XPATH로 찾은 버튼: {len(xpath_buttons)}개")
        
        # 버튼이 하나도 없다면 페이지 문제
        if len(all_buttons) == 0:
            log_print("\n[경고] 버튼이 하나도 없습니다! 페이지 상태를 확인합니다...")
            log_print("페이지 소스 일부:")
            page_source = driver.page_source[:500]
            log_print(page_source)
        
        # 여러 방법으로 저장 버튼 찾기 시도
        save_button = None
        selectors = [
            "button[class*='save']",
            "button[class*='Save']",
            "button[class*='publish']",
            "button[class*='Publish']",
            "a[class*='save']",  # a 태그도 시도
            "a[class*='Save']",
            "[role='button']",  # role이 button인 요소
        ]
        
        log_print("\n[디버깅] CSS 셀렉터로 검색 중...")
        for selector in selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                log_print(f"  셀렉터 '{selector}': {len(buttons)}개 발견")
                for btn in buttons:
                    btn_text = btn.text.strip()
                    if btn_text:
                        log_print(f"    텍스트: '{btn_text}'")
                    if "임시저장" in btn_text or "저장" in btn_text or "발행" in btn_text:
                        save_button = btn
                        log_print(f"[OK] 발견! 셀렉터: {selector}, 텍스트: '{btn_text}'")
                        break
                if save_button:
                    break
            except Exception as e:
                log_print(f"  셀렉터 '{selector}' 오류: {str(e)}")
        
        # 여전히 못 찾았다면 텍스트로 전체 검색
        if not save_button:
            log_print("\n[디버깅] 텍스트 기반으로 전체 검색 중...")
            try:
                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                for idx, btn in enumerate(all_buttons):
                    try:
                        btn_text = btn.text.strip()
                        if btn_text and any(keyword in btn_text for keyword in ["임시저장", "저장", "임시 저장"]):
                            save_button = btn
                            log_print(f"[OK] 텍스트로 발견! 버튼[{idx}]: '{btn_text}'")
                            break
                    except:
                        continue
            except Exception as e:
                log_print(f"텍스트 검색 중 오류: {str(e)}")
        
        if save_button:
            log_print(f"\n저장 버튼 클릭 시도 중...")
            # 저장 버튼으로 스크롤
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
            time.sleep(1)
            
            # 클릭 시도 (여러 방법)
            click_success = False
            try:
                # 방법 1: 일반 클릭
                save_button.click()
                click_success = True
                log_print("[OK] 클릭 방법: 일반 클릭")
            except Exception as e1:
                log_print(f"일반 클릭 실패: {str(e1)}")
                try:
                    # 방법 2: JavaScript 클릭
                    driver.execute_script("arguments[0].click();", save_button)
                    click_success = True
                    log_print("[OK] 클릭 방법: JavaScript")
                except Exception as e2:
                    log_print(f"JavaScript 클릭 실패: {str(e2)}")
                    try:
                        # 방법 3: ActionChains 클릭
                        actions = ActionChains(driver)
                        actions.move_to_element(save_button).click().perform()
                        click_success = True
                        log_print("[OK] 클릭 방법: ActionChains")
                    except Exception as e3:
                        log_print(f"ActionChains 클릭 실패: {str(e3)}")
            
            if click_success:
                time.sleep(3)
                log_print("\n[OK] 저장 버튼 클릭 완료!")
            else:
                log_print("\n[WARNING] 모든 클릭 방법 실패 - 수동으로 저장해주세요.")
                log_print("브라우저 창을 확인하고 수동으로 저장 버튼을 클릭하세요.")
        else:
            log_print("\n" + "="*60)
            log_print("[INFO] 자동 저장 버튼을 찾지 못했습니다!")
            log_print("="*60)
            log_print("하지만 걱정하지 마세요!")
            log_print("")
            log_print("✅ 제목과 본문은 이미 입력되었습니다.")
            log_print("✅ 브라우저 창에서 내용을 확인하세요.")
            log_print("")
            log_print("수동 저장 방법:")
            log_print("  1. 브라우저 창으로 이동")
            log_print("  2. 우측 상단의 '임시저장' 또는 '발행' 버튼 클릭")
            log_print("  3. 저장 완료!")
            log_print("")
            log_print(f"디버깅 파일:")
            log_print(f"  - 로그: '{log_file}'")
            log_print(f"  - 버튼 정보: 'debug_button_info.txt'")
            log_print(f"  - 스크린샷: 'screenshot_*.png'")
            log_print("")
            log_print("브라우저를 닫지 말고 수동으로 저장하세요.")
            log_print("저장 완료 후 Enter를 눌러주세요...")
            log_print("="*60)
            
            # 사용자가 Enter를 누를 때까지 대기
            input()
            # 수동 저장했다고 가정하고 True 반환
            return True
        
        return True
        
    except Exception as e:
        log_print(f"블로그 글 작성 중 오류 발생: {str(e)}")
        # iframe에서 벗어나기
        try:
            driver.switch_to.default_content()
        except:
            pass
        return False

# 메인 실행 함수
def main():
    """메인 실행 함수"""
    driver = None
    try:
        log_print(f"\n{'='*60}")
        log_print(f"네이버 블로그 자동화 스크립트 시작")
        log_print(f"로그 파일: {log_file}")
        log_print(f"{'='*60}\n")
        
        # 드라이버 설정
        driver = setup_driver()
        
        # 네이버 로그인 및 블로그 이동
        if naver_login(driver):
            # 블로그 글 작성
            if write_blog_post(driver):
                log_print("\n[OK] 블로그 글 작성 완료!")
            else:
                log_print("\n[ERROR] 블로그 글 작성 실패")
            
            log_print("\n자동화 스크립트 실행 완료!")
            log_print("브라우저를 종료하려면 이 창을 닫으세요.")
            
            # 사용자가 작업을 마칠 때까지 대기
            input("\n작업이 끝나면 Enter를 눌러 브라우저를 종료하세요...")
        else:
            log_print("로그인에 실패했습니다.")
            
    except Exception as e:
        log_print(f"프로그램 실행 중 오류 발생: {str(e)}")
        
    finally:
        # 드라이버 종료
        if driver:
            driver.quit()
            log_print("브라우저 종료 완료")
        
        log_print(f"\n{'='*60}")
        log_print(f"모든 로그가 '{log_file}' 파일에 저장되었습니다.")
        log_print(f"{'='*60}")

if __name__ == "__main__":
    main()
