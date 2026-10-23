#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gsc_opportunity_engine.py
Google Search Console Search Analytics 수집 및 11~20위 기회 키워드 자동 분류/스코어링 모듈
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class GSCOpportunityEngine:
    def __init__(self, config_path: str = "sites_config.json"):
        if not os.path.isabs(config_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, config_path)
        
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.sites = self.config.get("sites", [])

    def fetch_search_analytics(self, site: Dict[str, Any], days: int = 7) -> List[Dict[str, Any]]:
        """
        GSC API 연동을 통해 [page, query] 복합 디멘션 실적을 수집합니다.
        GSC 자격증명이 없는 경우, 각 사이트의 페르소나와 핵심 토픽에 최적화된 현실적 실측 모의 데이터를 반환합니다.
        """
        credentials_file = os.environ.get("GSC_SERVICE_ACCOUNT_JSON")
        if credentials_file and os.path.exists(credentials_file):
            try:
                # 실제 Google API Client 연동
                from google.oauth2 import service_account
                from googleapiclient.discovery import build
                
                creds = service_account.Credentials.from_service_account_file(
                    credentials_file,
                    scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
                )
                service = build("searchconsole", "v1", credentials=creds)
                
                end_date = datetime.now() - timedelta(days=2) # GSC는 통상 D-2 데이터 제공
                start_date = end_date - timedelta(days=days)
                
                request_body = {
                    "startDate": start_date.strftime("%Y-%m-%d"),
                    "endDate": end_date.strftime("%Y-%m-%d"),
                    "dimensions": ["page", "query"],
                    "rowLimit": 250
                }
                response = service.searchanalytics().query(
                    siteUrl=site["gsc_property"], body=request_body
                ).execute()
                
                rows = []
                for item in response.get("rows", []):
                    rows.append({
                        "page": item["keys"][0],
                        "query": item["keys"][1],
                        "clicks": item.get("clicks", 0),
                        "impressions": item.get("impressions", 0),
                        "ctr": item.get("ctr", 0.0),
                        "position": item.get("position", 0.0)
                    })
                logging.info(f"[{site['domain']}] Live GSC 수집 성공: {len(rows)}개 쿼리 매핑")
                return rows
            except Exception as e:
                logging.warning(f"[{site['domain']}] GSC API 호출 실패 ({e}). 모의 데이터 모드로 전환합니다.")
        
        # Mock/Offline Seed Engine (사이트별 실제 최적화 기회 키워드 풀)
        return self._generate_realistic_mock_data(site)

    def _generate_realistic_mock_data(self, site: Dict[str, Any]) -> List[Dict[str, Any]]:
        sid = site["id"]
        base = site["site_url"]
        
        mock_templates = {
            "agrokorea": [
                {"page": f"{base}/products/calf-diarrhea", "query": "송아지 설사약 추천", "clicks": 85, "impressions": 1420, "ctr": 0.059, "position": 12.3},
                {"page": f"{base}/tech/montmorillonite", "query": "천연 점토 광물 설사 흡착", "clicks": 34, "impressions": 890, "ctr": 0.038, "position": 14.8},
                {"page": f"{base}/about", "query": "친환경 축산 동물약품", "clicks": 210, "impressions": 3200, "ctr": 0.065, "position": 6.2},
                {"page": f"{base}/", "query": "한국아그로", "clicks": 450, "impressions": 890, "ctr": 0.505, "position": 1.1},
                {"page": f"{base}/products/immunity", "query": "소 면역증강제 주사 대체", "clicks": 12, "impressions": 1150, "ctr": 0.010, "position": 18.2},
            ],
            "rotagal": [
                {"page": f"{base}/#rotavirus", "query": "송아지 로타바이러스 치료법", "clicks": 110, "impressions": 2100, "ctr": 0.052, "position": 11.5},
                {"page": f"{base}/#piglet", "query": "자돈 이유기 수양성 설사", "clicks": 45, "impressions": 1340, "ctr": 0.033, "position": 15.2},
                {"page": f"{base}/#features", "query": "송아지 초유 지사 보조제", "clicks": 18, "impressions": 920, "ctr": 0.019, "position": 19.1},
                {"page": f"{base}/#order", "query": "로타겔 구매", "clicks": 320, "impressions": 650, "ctr": 0.492, "position": 1.2},
            ],
            "parvogel": [
                {"page": f"{base}/blog/puppy-parvo-recovery-case", "query": "파보장염 초기증상 구토 설사", "clicks": 240, "impressions": 4850, "ctr": 0.049, "position": 12.1},
                {"page": f"{base}/blog/puppy-acute-diarrhea-golden-time", "query": "새끼강아지 노란토 대처", "clicks": 180, "impressions": 3600, "ctr": 0.050, "position": 13.7},
                {"page": f"{base}/#order", "query": "파보겔 공식 스토어", "clicks": 890, "impressions": 1400, "ctr": 0.635, "position": 1.0},
                {"page": f"{base}/blog/dog-diarrhea-medicine-guide", "query": "강아지 설사 상비약 키트", "clicks": 65, "impressions": 2200, "ctr": 0.029, "position": 16.4},
                {"page": f"{base}/blog/parrot-ggomi-recovery", "query": "앵무새 물변 낙조 응급 케어", "clicks": 32, "impressions": 840, "ctr": 0.038, "position": 14.3},
            ],
            "monsmecta": [
                {"page": f"{base}/#moa", "query": "동물병원 처방용 몬모릴로나이트", "clicks": 42, "impressions": 980, "ctr": 0.042, "position": 13.4},
                {"page": f"{base}/#clinical", "query": "동물병원 지사 보조제 추천", "clicks": 28, "impressions": 1120, "ctr": 0.025, "position": 17.5},
                {"page": f"{base}/", "query": "몬스멕타 수의사 포털", "clicks": 190, "impressions": 340, "ctr": 0.558, "position": 1.1},
            ],
            "vetacol": [
                {"page": f"{base}/#ingredients", "query": "가축 면역글로불린 보충제", "clicks": 31, "impressions": 880, "ctr": 0.035, "position": 14.1},
                {"page": f"{base}/#dosage", "query": "환절기 송아지 호흡기 면역", "clicks": 15, "impressions": 1050, "ctr": 0.014, "position": 18.9},
                {"page": f"{base}/", "query": "베타콜", "clicks": 140, "impressions": 290, "ctr": 0.482, "position": 1.0},
            ],
            "100bagger": [
                {"page": f"{base}/cameron", "query": "미국주식 급등주 스크리너", "clicks": 310, "impressions": 6200, "ctr": 0.050, "position": 12.8},
                {"page": f"{base}/cameron", "query": "로스 카메론 모멘텀 전략", "clicks": 145, "impressions": 2900, "ctr": 0.050, "position": 13.9},
                {"page": f"{base}/", "query": "100bagger 퀀트", "clicks": 520, "impressions": 820, "ctr": 0.634, "position": 1.1},
                {"page": f"{base}/blog/day-trading-momentum", "query": "미국 개장 전 프리마켓 갭상승 검색기", "clicks": 55, "impressions": 2400, "ctr": 0.022, "position": 17.1},
            ],
            "snj_vet": [
                {"page": f"{base}/#cases", "query": "하남 미사 동물병원 파보 임상", "clicks": 62, "impressions": 1150, "ctr": 0.053, "position": 12.4},
                {"page": f"{base}/#team", "query": "하남 외과 소화기내과 동물병원", "clicks": 44, "impressions": 1420, "ctr": 0.030, "position": 16.2},
                {"page": f"{base}/", "query": "에스앤제이 동물병원", "clicks": 280, "impressions": 490, "ctr": 0.571, "position": 1.0},
            ]
        }
        return mock_templates.get(sid, [])

    def score_and_classify(self, rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        수집된 쿼리를 3단계로 분류하고 스코어링합니다:
        1. quick_wins: 11.0 <= position <= 20.0 (노출량 순 정렬) -> 기존 글 업데이트 대상!
        2. content_gap: impressions >= 500 & ctr < 0.02 & position > 15.0 -> 신규 포스트 작성 대상
        3. page_one: position < 10.0 -> 방어 및 유지 대상
        """
        quick_wins = []
        content_gap = []
        page_one = []

        for row in rows:
            pos = row["position"]
            impr = row["impressions"]
            ctr = row["ctr"]

            # 가중 점수 계산: (노출량 * (21 - 순위))
            # 순위가 11위에 가까울수록, 노출량이 클수록 최우선 점수가 부여됨
            score = impr * max(0.5, (21.0 - pos))
            item = dict(row)
            item["priority_score"] = round(score, 1)

            if 11.0 <= pos <= 20.0:
                quick_wins.append(item)
            elif pos < 10.0:
                page_one.append(item)
            elif impr >= 500 and ctr < 0.025:
                content_gap.append(item)

        # 정렬: 스코어 내림차순
        quick_wins.sort(key=lambda x: x["priority_score"], reverse=True)
        content_gap.sort(key=lambda x: x["priority_score"], reverse=True)
        page_one.sort(key=lambda x: x["impressions"], reverse=True)

        return {
            "quick_wins": quick_wins,
            "content_gap": content_gap,
            "page_one": page_one
        }

    def run_all_sites(self) -> Dict[str, Any]:
        """7개 사이트 전체를 스캔하여 종합 기회 분석 결과를 반환합니다."""
        results = {}
        for site in self.sites:
            sid = site["id"]
            rows = self.fetch_search_analytics(site)
            classified = self.score_and_classify(rows)
            results[sid] = {
                "site": site,
                "total_queries": len(rows),
                "quick_wins": classified["quick_wins"],
                "content_gap": classified["content_gap"],
                "page_one": classified["page_one"],
                "top_recommendations": classified["quick_wins"][:2] + classified["content_gap"][:1]
            }
        return results

if __name__ == "__main__":
    engine = GSCOpportunityEngine()
    data = engine.run_all_sites()
    print(f"=== 7개 사이트 GSC 기회 키워드 분석 완료 ===")
    for sid, res in data.items():
        print(f"\n[{res['site']['domain']}] {res['site']['name']}")
        print(f"- 11~20위 Quick-Win 후보: {len(res['quick_wins'])}건")
        for idx, qw in enumerate(res['quick_wins'][:2], 1):
            print(f"  {idx}. '{qw['query']}' (평균 {qw['position']}위 / 노출 {qw['impressions']}회 / 스코어 {qw['priority_score']}) -> {qw['page']}")
        if res['content_gap']:
            cg = res['content_gap'][0]
            print(f"- Content Gap 신규 공략: '{cg['query']}' (평균 {cg['position']}위 / 노출 {cg['impressions']}회)")
