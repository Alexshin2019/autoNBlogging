"""
엑셀 파일 생성 스크립트
posting.xlsx 파일을 생성하고 블로그 포스팅 템플릿을 작성합니다.
"""

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
import os

def create_posting_excel():
    """포스팅용 엑셀 파일을 생성하는 함수"""
    
    # 새 워크북 생성
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "포스팅목록"
    
    # 헤더 작성 (A1: 제목, B1: 본문)
    sheet['A1'] = "제목"
    sheet['B1'] = "본문"
    
    # 헤더 스타일 적용
    header_font = Font(bold=True, size=12)
    header_alignment = Alignment(horizontal='center', vertical='center')
    
    sheet['A1'].font = header_font
    sheet['A1'].alignment = header_alignment
    sheet['B1'].font = header_font
    sheet['B1'].alignment = header_alignment
    
    # 검색 가능한 블로그 제목 샘플 5개
    blog_titles = [
        "2026년 초보자를 위한 파이썬 프로그래밍 완벽 가이드",
        "ChatGPT와 AI 활용법 - 업무 효율 10배 높이는 실전 팁",
        "엑셀 자동화로 반복 업무 없애는 방법 (Python 활용)",
        "블로그 수익화 성공 전략 - 월 100만원 달성 후기",
        "VSCode 필수 확장 프로그램 추천 TOP 10 (2026년 최신)"
    ]
    
    # A2~A6에 제목 샘플 입력
    for idx, title in enumerate(blog_titles, start=2):
        sheet[f'A{idx}'] = title
    
    # 열 너비 조정 (가독성 향상)
    sheet.column_dimensions['A'].width = 60
    sheet.column_dimensions['B'].width = 80
    
    # 파일 저장 경로 설정
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, "posting.xlsx")
    
    # 파일 저장
    workbook.save(file_path)
    workbook.close()
    
    print(f"✅ 엑셀 파일이 성공적으로 생성되었습니다!")
    print(f"📂 저장 위치: {file_path}")
    print(f"📝 생성된 제목 샘플: {len(blog_titles)}개")

if __name__ == "__main__":
    try:
        create_posting_excel()
    except Exception as error:
        print(f"❌ 오류 발생: {error}")
        print("💡 openpyxl 라이브러리가 설치되어 있는지 확인하세요.")
        print("   설치 명령: pip install openpyxl")
