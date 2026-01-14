# -*- coding: utf-8 -*-
import os
import sys

# Windows 콘솔 인코딩 설정 (GUI 모드에서는 건너뜀)
if sys.platform == "win32" and sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from google import genai

class GeminiAPI:
    """Gemini API를 사용하기 위한 클래스"""
    
    def __init__(self, api_key=None):
        """
        Gemini API 클라이언트 초기화
        
        Args:
            api_key: Gemini API 키 (None이면 환경변수에서 가져옴)
        """
        # API 키 설정
        if api_key:
            os.environ['GEMINI_API_KEY'] = api_key
        elif 'GEMINI_API_KEY' not in os.environ:
            raise ValueError("API 키가 제공되지 않았습니다. api_key 매개변수나 GEMINI_API_KEY 환경변수를 설정해주세요.")
        
        # 클라이언트 초기화
        try:
            self.client = genai.Client(api_key=api_key or os.environ.get('GEMINI_API_KEY'))
            self.model_name = "gemini-2.0-flash-exp"
            print(f"[OK] Gemini API 클라이언트 초기화 완료 (모델: {self.model_name})")
        except Exception as error:
            raise Exception(f"Gemini API 초기화 실패: {str(error)}")
    
    def generate_content(self, prompt, temperature=1.0, max_output_tokens=8192):
        """
        텍스트 생성 요청
        
        Args:
            prompt: 생성할 텍스트의 프롬프트
            temperature: 생성 다양성 (0.0 ~ 2.0, 높을수록 창의적)
            max_output_tokens: 최대 출력 토큰 수
            
        Returns:
            생성된 텍스트 문자열
        """
        try:
            print(f"\n[생성 요청] 프롬프트: {prompt[:100]}...")
            
            # 생성 설정
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            }
            
            # API 호출
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=generation_config
            )
            
            # 응답 텍스트 추출
            result_text = response.text
            print(f"[OK] 생성 완료 (길이: {len(result_text)}자)")
            
            return result_text
            
        except Exception as error:
            print(f"[ERROR] 텍스트 생성 중 오류 발생: {str(error)}")
            raise
    
    def generate_blog_post(self, topic, style="친근하고 정보적인", word_count=1000):
        """
        블로그 글 생성
        
        Args:
            topic: 블로그 글 주제
            style: 글 스타일
            word_count: 목표 단어 수
            
        Returns:
            생성된 블로그 글
        """
        prompt = f"""
다음 주제로 전문적인 블로그 글을 작성해주세요:

주제: {topic}
스타일: {style}
목표 길이: 약 {word_count}자

필수 구성 요소:
1. 매력적이고 클릭하고 싶은 제목 (감탄사나 질문형)
2. 본문 최상단: "※ 본 글은 2025년 9월 4일 기준 최신 정보를 바탕으로 작성되었습니다."
3. 도입부: 주제와 관련된 공감 가는 상황 설명
4. "✔ 이런 분들께 추천합니다!" 섹션 (4-5개 항목)
5. "📌 목차" 섹션 (5-6개 항목) - 각 목차 항목은 클릭 가능한 링크로 만들 것
6. "🔍 전체 요약" 섹션 (2-3줄)
7. 본문 내용 (3-5개의 소제목으로 구성, 각 소제목은 구체적이고 실용적인 정보 포함)
   - 각 소제목은 큰 글씨와 굵게로 강조할 것
   - 소제목에는 앵커 ID를 부여할 것
8. "자주 묻는 질문(FAQ)" 섹션 (5개의 질문과 답변)
9. "📌 참고할 만한 사이트" 섹션 (5개 링크 - 쿠팡, 네이버쇼핑 등)
10. "📝 마무리 요약 및 실천 유도" 섹션
11. 마지막: "※ 본 글은 다양한 공식 자료를 바탕으로 작성되었으나, 작성자도 오류가 있을 수 있으며 모든 내용은 참고용입니다..."

작성 규칙:
- 마크다운 문법(#, **, *, _)을 절대 사용하지 말 것
- HTML 태그를 사용하여 구조화할 것
- 각 섹션은 명확하게 구분
- 친근하면서도 전문적인 어투
- 구체적인 예시와 팁 포함
- 실용적이고 도움되는 정보 중심

출력 형식 (HTML 태그 사용, 모든 텍스트는 왼쪽 정렬):
제목: [매력적인 제목]

<p style="text-align: left;">※ 본 글은 2025년 9월 4일 기준 최신 정보를 바탕으로 작성되었습니다.</p>

<p style="text-align: left;">[도입부 문단]</p>

<p style="text-align: left;"><strong>✔ 이런 분들께 추천합니다!</strong></p>
<ul style="text-align: left;">
<li>[추천 대상 1]</li>
<li>[추천 대상 2]</li>
<li>[추천 대상 3]</li>
<li>[추천 대상 4]</li>
</ul>

<p style="text-align: left;"><strong>📌 목차</strong></p>
<ul style="text-align: left;">
<li><a href="#section1">[목차 1]</a></li>
<li><a href="#section2">[목차 2]</a></li>
<li><a href="#section3">[목차 3]</a></li>
<li><a href="#section4">[목차 4]</a></li>
<li><a href="#section5">[목차 5]</a></li>
</ul>

<p style="text-align: left;"><strong>🔍 전체 요약</strong></p>
<p style="text-align: left;">[2-3줄 요약]</p>

<h2 id="section1" style="font-size: 20px; font-weight: bold; color: #333; margin-top: 30px; text-align: left;">[소제목 1]</h2>
<p style="text-align: left;">[내용...]</p>

<h2 id="section2" style="font-size: 20px; font-weight: bold; color: #333; margin-top: 30px; text-align: left;">[소제목 2]</h2>
<p style="text-align: left;">[내용...]</p>

<h2 id="section3" style="font-size: 20px; font-weight: bold; color: #333; margin-top: 30px; text-align: left;">[소제목 3]</h2>
<p style="text-align: left;">[내용...]</p>

<p style="text-align: left;"><strong>자주 묻는 질문(FAQ)</strong></p>
<p style="text-align: left;"><strong>Q: [질문 1]</strong><br>
A: [답변 1]</p>

<p style="text-align: left;"><strong>Q: [질문 2]</strong><br>
A: [답변 2]</p>

<p style="text-align: left;"><strong>Q: [질문 3]</strong><br>
A: [답변 3]</p>

<p style="text-align: left;"><strong>Q: [질문 4]</strong><br>
A: [답변 4]</p>

<p style="text-align: left;"><strong>Q: [질문 5]</strong><br>
A: [답변 5]</p>

<p style="text-align: left;"><strong>📌 참고할 만한 사이트</strong></p>
<ul style="text-align: left;">
<li><a href="https://www.coupang.com" target="_blank">쿠팡 공식 쇼핑몰</a></li>
<li><a href="https://shopping.naver.com" target="_blank">네이버 스마트스토어</a></li>
<li>[관련 사이트 3]</li>
<li>[관련 사이트 4]</li>
<li>[관련 사이트 5]</li>
</ul>

<p style="text-align: left;"><strong>📝 마무리 요약 및 실천 유도</strong></p>
<p style="text-align: left;">[마무리 문단 및 행동 촉구]</p>

<p style="text-align: left;">※ 본 글은 다양한 공식 자료를 바탕으로 작성되었으나, 작성자도 오류가 있을 수 있으며 모든 내용은 참고용입니다. 최종 신청 전에는 반드시 관련 기관의 공식 공고문을 통해 정확한 정보를 확인하시기 바랍니다.</p>

블로그 글을 작성해주세요:
"""
        
        return self.generate_content(prompt)
    
    def summarize_text(self, text, max_sentences=5):
        """
        텍스트 요약
        
        Args:
            text: 요약할 텍스트
            max_sentences: 최대 문장 수
            
        Returns:
            요약된 텍스트
        """
        prompt = f"""
다음 텍스트를 {max_sentences}개 문장 이내로 요약해주세요:

{text}

요약:
"""
        
        return self.generate_content(prompt, temperature=0.3)
    
    def translate_text(self, text, target_language="한국어"):
        """
        텍스트 번역
        
        Args:
            text: 번역할 텍스트
            target_language: 목표 언어
            
        Returns:
            번역된 텍스트
        """
        prompt = f"""
다음 텍스트를 {target_language}로 번역해주세요:

{text}

번역:
"""
        
        return self.generate_content(prompt, temperature=0.3)
    
    def improve_writing(self, text):
        """
        글쓰기 개선
        
        Args:
            text: 개선할 텍스트
            
        Returns:
            개선된 텍스트
        """
        prompt = f"""
다음 텍스트의 맞춤법, 문법, 표현을 개선해주세요.
더 자연스럽고 읽기 쉽게 다듬어주세요:

{text}

개선된 버전:
"""
        
        return self.generate_content(prompt, temperature=0.5)


# 사용 예시
def main():
    """메인 실행 함수"""
    # API 키 설정 (실제 사용 시 환경변수 사용 권장)
    api_key = "AIzaSyD1Iih0tQ528MxCBhV8yhmi7wHBc7nZnac"
    
    try:
        # Gemini API 초기화
        gemini = GeminiAPI(api_key=api_key)
        
        # 예시 1: 간단한 질문
        print("\n" + "="*50)
        print("예시 1: 간단한 질문")
        print("="*50)
        response = gemini.generate_content("인공지능이 무엇인지 한 문장으로 설명해주세요.")
        print(f"\n답변: {response}")
        
        # 예시 2: 블로그 글 생성
        print("\n" + "="*50)
        print("예시 2: 블로그 글 생성")
        print("="*50)
        blog_post = gemini.generate_blog_post(
            topic="내 지식으로 돈 벌기, 왜 전자책이 답일까요?",
            style="초보자를 위한 친절한",
            word_count=500
        )
        print(f"\n생성된 블로그 글:\n{blog_post}")
        
        # 예시 3: 텍스트 요약
        print("\n" + "="*50)
        print("예시 3: 텍스트 요약")
        print("="*50)
        long_text = """
        인공지능은 인간의 학습능력, 추론능력, 지각능력을 인공적으로 구현한 컴퓨터 시스템입니다.
        최근 딥러닝 기술의 발전으로 이미지 인식, 음성 인식, 자연어 처리 등 다양한 분야에서 
        인간 수준 또는 그 이상의 성능을 보이고 있습니다. 특히 ChatGPT와 같은 대화형 AI는 
        일상생활에서 널리 활용되고 있으며, 교육, 의료, 금융, 제조업 등 거의 모든 산업 분야에 
        혁신을 가져오고 있습니다.
        """
        summary = gemini.summarize_text(long_text, max_sentences=2)
        print(f"\n요약: {summary}")
        
        # 예시 4: 글쓰기 개선
        print("\n" + "="*50)
        print("예시 4: 글쓰기 개선")
        print("="*50)
        original_text = "오늘 날씨가 너무 좋아서 산책을 했어요. 공원에 가니까 사람들이 많았고 꽃도 예뻤어요."
        improved = gemini.improve_writing(original_text)
        print(f"\n원본: {original_text}")
        print(f"개선: {improved}")
        
    except Exception as error:
        print(f"\n[ERROR] 오류 발생: {str(error)}")


if __name__ == "__main__":
    main()
