# -*- coding: utf-8 -*-
import openpyxl
from openpyxl.styles import Font, Alignment

# 새 엑셀 파일 생성
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "블로그 포스팅"

# 1행: 헤더
sheet['A1'] = "제목"
sheet['B1'] = "본문"

# 헤더 스타일 설정
for cell in ['A1', 'B1']:
    sheet[cell].font = Font(bold=True, size=12)
    sheet[cell].alignment = Alignment(horizontal='center', vertical='center')

# 2행부터: 샘플 데이터
sample_posts = [
    {
        "title": "파이썬으로 엑셀 자동화하기",
        "content": """오늘은 파이썬으로 엑셀을 자동화하는 방법에 대해 알아보겠습니다.

openpyxl 라이브러리를 사용하면 엑셀 파일을 쉽게 읽고 쓸 수 있습니다.

반복 작업을 자동화하여 업무 효율을 높일 수 있습니다."""
    },
    {
        "title": "셀레니움으로 웹 자동화 시작하기",
        "content": """셀레니움은 웹 브라우저를 자동으로 제어할 수 있는 도구입니다.

로그인, 클릭, 입력 등 모든 작업을 자동화할 수 있습니다.

반복적인 웹 작업을 자동화하면 시간을 크게 절약할 수 있습니다."""
    },
    {
        "title": "네이버 블로그 자동 포스팅 방법",
        "content": """네이버 블로그에 자동으로 글을 올리는 방법을 알아봅니다.

셀레니움과 파이썬을 활용하면 쉽게 자동화할 수 있습니다.

매일 반복되는 포스팅 작업을 자동화해보세요."""
    }
]

# 샘플 데이터 입력
for idx, post in enumerate(sample_posts, start=2):
    sheet[f'A{idx}'] = post['title']
    sheet[f'B{idx}'] = post['content']

# 열 너비 조정
sheet.column_dimensions['A'].width = 40
sheet.column_dimensions['B'].width = 80

# 파일 저장
filename = "posting.xlsx"
workbook.save(filename)

print(f"✓ '{filename}' 파일이 생성되었습니다!")
print(f"✓ 총 {len(sample_posts)}개의 샘플 데이터가 입력되었습니다.")
print("\n[파일 내용]")
for idx, post in enumerate(sample_posts, start=1):
    print(f"{idx}. 제목: {post['title']}")
    print(f"   본문: {post['content'][:50]}...\n")
