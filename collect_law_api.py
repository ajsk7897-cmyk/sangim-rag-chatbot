import os
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import re

# 국가법령정보센터 Open API 판례 검색
# 발급받은 실제 API 키가 있다면 아래 변수에 입력해 주세요. (현재는 테스트키 'test' 사용)
API_KEY = "920400"  
QUERY = "상가건물 임대차보호법"
BASE_URL = "https://www.law.go.kr/DRF/lawSearch.do"

def collect_precedents():
    print(f"국가법령정보센터 Open API에서 '{QUERY}' 관련 판례 수집을 시작합니다...")
    
    # 1. 판례 목록(List) 조회
    params = {
        "OC": API_KEY,
        "target": "prec",
        "type": "XML",
        "query": QUERY,
        "display": 50 # 한 번에 가져올 최대 건수 (50건)
    }
    
    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        print(f"API 호출 실패: 상태 코드 {response.status_code}")
        return False
        
    try:
        root = ET.fromstring(response.content)
    except Exception as e:
        print(f"XML 파싱 에러: {e}")
        return False
        
    prec_seqs = []
    for prec in root.findall('.//prec'):
        prec_seq = prec.find('판례일련번호').text if prec.find('판례일련번호') is not None else None
        if prec_seq:
            prec_seqs.append(prec_seq)
            
    print(f"총 {len(prec_seqs)}건의 최신/관련 판례 목록을 찾았습니다. 상세 내용을 조회합니다...")
    
    # 기존 데이터 로드 (중복 제거용)
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "RAG 백데이터"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "레퍼런스7. API자동수집_상임법판례모음.txt"
    
    existing_content = ""
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            existing_content = f.read()

    # 2. 판례 상세 내용(Detail) 조회 및 텍스트 취합
    all_texts = []
    if not existing_content:
        all_texts.append(f"--- 국가법령정보센터 '{QUERY}' 관련 주요 판례 모음 ---")
    
    detail_url = "https://www.law.go.kr/DRF/lawService.do"
    new_count = 0
    
    for seq in prec_seqs:
        det_params = {
            "OC": API_KEY,
            "target": "prec",
            "ID": seq,
            "type": "XML"
        }
        res = requests.get(detail_url, params=det_params)
        if res.status_code == 200:
            try:
                d_root = ET.fromstring(res.content)
                case_name = d_root.find('.//사건명').text if d_root.find('.//사건명') is not None else "사건명 없음"
                case_no = d_root.find('.//사건번호').text if d_root.find('.//사건번호') is not None else "사건번호 없음"
                
                # 중복 검사 (사건번호가 이미 기존 파일에 존재하면 건너뜀)
                if case_no != "사건번호 없음" and f"({case_no})" in existing_content:
                    continue
                
                # 판결요지와 판시사항
                summary = d_root.find('.//판결요지').text if d_root.find('.//판결요지') is not None else ""
                points = d_root.find('.//판시사항').text if d_root.find('.//판시사항') is not None else ""
                
                # HTML 태그 제거 및 CDATA 정리
                content = summary if summary else points
                content = re.sub('<[^<]+>', '', content) if content else "판결요지/판시사항 내용 없음"
                content = content.replace("<![CDATA[", "").replace("]]>", "").strip()
                
                doc_text = f"\n[판례] {case_name} ({case_no})\n요지 및 핵심사항:\n{content}\n"
                all_texts.append(doc_text)
                new_count += 1
            except Exception as e:
                print(f"상세 조회 파싱 에러 (일련번호 {seq}): {e}")
                
    # 3. RAG 백데이터 폴더에 저장 (누적 저장 모드 'a')
    if new_count > 0:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write("\n".join(all_texts) + "\n")
        print(f"수집 완료: 기존 데이터에 {new_count}건의 새로운 판례가 누적 추가되었습니다.")
    else:
        print("수집 완료: 이미 모든 최신 판례가 누적되어 있어 추가할 항목이 없습니다.")
    return True

if __name__ == "__main__":
    collect_precedents()
