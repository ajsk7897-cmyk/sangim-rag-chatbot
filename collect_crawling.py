import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# 김앤장 '부동산' 관련 인사이트/뉴스 웹 크롤러 모듈
# (참고: 김앤장 공식 홈페이지는 보안 및 동적 렌더링(JS) 차단으로 인해 직접 크롤링이 어려워, 
# 가장 정확하고 안정적인 포털(네이버)의 '김앤장 부동산' 검색 결과를 공식 레퍼런스로 대리 수집합니다.)

def collect_news():
    print("웹 크롤링(김앤장 인사이트 - '부동산' 관련 공식 배포 자료)을 시작합니다...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # 타겟: 네이버 뉴스에서 김앤장 법률사무소가 배포/언급된 부동산 관련 최신 인사이트
    target_url = "https://search.naver.com/search.naver?where=news&query=김앤장+부동산+법률+OR+인사이트"
    
    try:
        response = requests.get(target_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 기사 제목과 요약문 추출
        articles = soup.find_all("a", class_="news_tit")
        desc = soup.find_all("a", class_="api_txt_lines dsc_txt_wrap")
        
        # 기존 데이터 로드
        base_dir = Path(__file__).resolve().parent.parent
        data_dir = base_dir / "RAG 백데이터"
        data_dir.mkdir(parents=True, exist_ok=True)
        output_path = data_dir / "레퍼런스8. 크롤링수집_김앤장부동산.txt"
        
        existing_content = ""
        if output_path.exists():
            with open(output_path, "r", encoding="utf-8") as f:
                existing_content = f.read()

        all_texts = []
        if not existing_content:
            all_texts.append("--- 웹 크롤링: 김앤장 법률사무소 '부동산' 관련 최근 인사이트 및 기사 요약 ---")
        
        new_count = 0
        for idx in range(min(len(articles), len(desc))):
            title = articles[idx].text.strip()
            link = articles[idx]["href"]
            summary = desc[idx].text.strip()
            
            # 중복 검사 (제목이나 링크가 이미 기존 파일에 존재하면 건너뜀)
            if link in existing_content or title in existing_content:
                continue
            
            doc_text = f"\n[김앤장 관련 인사이트/기사] {title}\n주요내용: {summary}\n참조링크: {link}\n"
            all_texts.append(doc_text)
            new_count += 1
            
        # RAG 백데이터 폴더에 저장 (누적 저장 모드 'a')
        if new_count > 0:
            with open(output_path, "a", encoding="utf-8") as f:
                f.write("\n".join(all_texts) + "\n")
            print(f"수집 완료: 기존 데이터에 {new_count}건의 최신 기사가 누적 추가되었습니다.")
        else:
            print("수집 완료: 이미 모든 최신 기사가 누적되어 있어 추가할 항목이 없습니다.")
            
        return True
        
    except Exception as e:
        print(f"크롤링 중 에러 발생: {e}")
        return False

if __name__ == "__main__":
    collect_news()
