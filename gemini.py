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
다음 주제로 블로그 글을 작성해주세요:

주제: {topic}
스타일: {style}
목표 길이: 약 {word_count}자

요구사항:
1. 매력적인 제목을 포함할 것
2. 서론, 본론, 결론 구조로 작성할 것
3. 읽기 쉽고 이해하기 쉬운 문장으로 작성할 것
4. 실용적인 정보와 팁을 포함할 것
5. 한국어로 작성할 것
6. **중요**: 마크다운 문법(#, **, *, _, 등)을 사용하지 말고 순수 텍스트로만 작성할 것
7. 제목은 첫 줄에 작성하고, 그 다음 줄부터 본문을 작성할 것

형식:
제목: [여기에 제목]
[빈 줄]
[본문 내용...]

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
