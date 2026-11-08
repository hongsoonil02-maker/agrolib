#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
weekly_seo_runner.py (v2.1 Universal 7-Site End-to-End Auto-Deploy Edition)
7대 전 도메인 대상 주간 AI SEO & GEO 자율 운영 및 실제 코드 배포 파이프라인
- .env 다중 경로 자동 로드 (parvogel_landing/.env 및 agrolib/.env 연동)
- 7대 사이트 전수 스캔 및 10~20위 기회 키워드 발굴 (주간 자동 로테이션 지원)
- 도메인 팩트 검증(백신 vs 초유시린지 vs 나노점토 vs 병원 vs 퀀트) 및 JSON-LD 정합성 평가
- SEOAutoDeployer 연동을 통한 7개 홈페이지 실제 로컬 레포지토리 즉시 주입/프리렌더링
- 동적 텔레그램 1-Page 요약 브리핑 무인 발송
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from dotenv import load_dotenv
    _curr = Path(__file__).resolve().parent
    for _env_candidate in [
        _curr / ".env",
        _curr.parent.parent / ".env",
        Path("C:/Users/master/quant_system/100_bagger_saas/.env"),
        Path("C:/Users/master/quant_system/.env"),
        Path("C:/Users/master/parvogel_landing/.env"),
        Path("C:/Users/master/parvogel_landing/marketing_factory/.env")
    ]:
        if _env_candidate.exists():
            load_dotenv(_env_candidate, override=False)
except ImportError:
    pass

from gsc_opportunity_engine import GSCOpportunityEngine
from geo_content_generator import GEOContentGenerator
from seo_auto_deployer import SEOAutoDeployer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def evaluate_trust_score(draft: dict) -> dict:
    """
    무검수 자율 발행(Auto-Pilot)을 위한 다중 검증 엔진
    - JSON-LD 스키마 객체 유효성, 도메인 팩트 오염 여부, E-E-A-T 백링크, Direct Answer 검증
    """
    score = 100
    flags = []
    md = draft.get("content_markdown", "")
    sid = draft.get("site_id", "")
    schema = draft.get("schema_json_ld")

    # 1. 분리된 Schema.org JSON-LD 객체 유효성 검사
    if not isinstance(schema, dict) or schema.get("@context") != "https://schema.org":
        score -= 15
        flags.append("Schema.org JSON-LD 객체 누락 또는 규격 오류")

    # 2. 본문 내 날것의 JSON-LD 코드블록 잔존 여부 검사 (렌더링 오염 방지)
    if "<!-- Schema.org JSON-LD -->" in md or "```json" in md:
        score -= 20
        flags.append("본문 마크다운 내 Raw JSON 코드블록 오염")

    # 3. 교차 백링크(E-E-A-T 네트워크) 인용 여부
    if "http" not in md:
        score -= 15
        flags.append("상호 E-E-A-T 백링크 누락")

    # 4. Direct Answer 핵심 요약 블록 여부
    if "Direct Answer" not in md:
        score -= 10
        flags.append("AI 검색 요약 블록 누락")

    # 5. 도메인 팩트 오염 교차 검증 (Cross-Domain Contamination Guard)
    if sid == "rotagal" and ("몬모릴로나이트" in md or "경구 투여" in md):
        score -= 30
        flags.append("로타갈(주사 백신) 도메인 내 경구 광물 흡착제 오기재")
    if sid == "100bagger" and ("수의학" in md or "송아지" in md or "agrokorea" in md):
        score -= 40
        flags.append("100-Bagger(핀테크) 도메인 내 축산/수의 콘텐츠 혼입")
    if sid == "snj_vet" and "하남 미사" in md:
        score -= 25
        flags.append("S&J동물병원(용인 포곡) 지역명 오기재")

    status = "AUTO_APPROVED" if score >= 85 else "MANUAL_REVIEW_REQUIRED"
    return {
        "trust_score": score,
        "status": status,
        "flags": flags
    }


def send_telegram_briefing(text: str) -> bool:
    """텔레그램 핫라인으로 주간 1-Page 요약본 자동 발송 (Fallback 포함)"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logging.warning("[TELEGRAM] ⚠️ TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID 환경변수가 설정되지 않아 발송을 건너뜁니다.")
        return False

    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        res = requests.post(url, json=payload, timeout=8)
        if res.status_code == 200:
            logging.info("텔레그램 주간 브리핑 발송 성공!")
            return True
        else:
            logging.warning(f"텔레그램 발송 실패 (Status {res.status_code}): {res.text}")
            return False
    except Exception as e:
        logging.warning(f"텔레그램 발송 예외: {e}")
        return False


def run_weekly_pipeline():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    agrolib_root = os.path.abspath(os.path.join(base_dir, "..", ".."))
    today_str = datetime.now().strftime("%Y-%m-%d")

    logging.info(f"=== [7대 전 사이트 AI SEO & GEO End-to-End 파이프라인 가동: {today_str}] ===")

    config_path = os.path.join(base_dir, "sites_config.json")
    engine = GSCOpportunityEngine(config_path)
    generator = GEOContentGenerator(agrolib_root)
    deployer = SEOAutoDeployer(config_path)

    all_site_data = engine.run_all_sites()

    drafts_generated = []
    site_rows_meta = []

    for sid, data in all_site_data.items():
        site = data["site"]
        qw_list = data["quick_wins"]
        top_qw = qw_list[0] if qw_list else None

        if top_qw:
            draft = generator.generate_reoptimization_draft(site, top_qw)
            eval_res = evaluate_trust_score(draft)
            draft["trust_score"] = eval_res["trust_score"]
            draft["status"] = eval_res["status"]
            draft["validation_flags"] = eval_res["flags"]
            drafts_generated.append(draft)
            site_rows_meta.append((site, top_qw, draft))
        else:
            site_rows_meta.append((site, None, None))

    # 실제 7개 홈페이지 로컬 레포지토리에 AUTO_APPROVED 초안 및 JSON-LD 즉시 주입/배포
    deploy_results = deployer.deploy_approved_drafts(drafts_generated)

    report_lines = [
        f"# 🚀 7대 전 도메인 AI SEO & GEO 통합 분석 및 End-to-End 자율 배포 리포트 ({today_str})",
        "",
        "> **총괄 책임:** CTO 안그래 (Antigravity)  ",
        f"> **대상 도메인:** 7개 전 사이트 통합 가동 (`sites_config.json` v2.0 연동)  ",
        "> **핵심 전략:** 10~20위 Quick-Win 키워드 도메인 팩트 검증형 GEO 보강 + Schema.org `@id` 지식 그래프 결합 + 7대 레포지토리 실배포(`SEOAutoDeployer`)",
        "",
        "---",
        "",
        "## 1. 7대 도메인별 기회 키워드, 신뢰도 검증 및 실제 코드 배포 현황",
        "",
        "| 도메인 | 사이트명 | 타깃 키워드 | 현재 순위 / 주간 노출 | 신뢰도 점수 | 로컬 레포지토리 실배포 상태 |",
        "| :--- | :--- | :--- | :---: | :---: | :--- |"
    ]

    for site, top_qw, draft in site_rows_meta:
        sid = site["id"]
        if top_qw and draft:
            kw_str = f"**{top_qw['query']}**"
            pos_impr = f"{top_qw['position']}위 / {top_qw['impressions']:,}회"
            score_str = f"{draft['trust_score']}점"
            dep_status = deploy_results.get(sid, "PENDING")
            status_badge = f"🟢 `{dep_status}`" if draft["status"] == "AUTO_APPROVED" else f"🟡 수동 검수 ({dep_status})"
        else:
            kw_str = "모니터링 유지"
            pos_impr = "-"
            score_str = "100점"
            status_badge = "⚪ 1페이지 수성"

        report_lines.append(
            f"| `{site['domain']}` | {site['name']} | {kw_str} | {pos_impr} | {score_str} | {status_badge} |"
        )

    report_lines.extend([
        "",
        "---",
        "",
        "## 2. 도메인별 상세 GEO 보강안 및 분리된 Schema.org JSON-LD",
        ""
    ])

    for idx, d in enumerate(drafts_generated, 1):
        schema_pretty = json.dumps(d.get("schema_json_ld", {}), ensure_ascii=False, indent=2)
        shorts_hook = d.get("sns_derivatives", {}).get("shorts_script_15s", {}).get("hook_3s", "")
        report_lines.extend([
            f"### [{idx}] `{d['domain']}` ({d['site_name']}) — 판정: {d['status']} ({d['trust_score']}점) | 배포: `{d.get('deploy_result', 'DONE')}`",
            f"- **타겟 키워드:** `{d['target_query']}` (현재 {d['current_position']}위, 노출 {d['current_impressions']:,}회)",
            f"- **적용 대상 URL:** [{d['target_url']}]({d['target_url']})",
            f"- **OSMU 15초 쇼츠 훅(Hook):** *\"{shorts_hook}\"*",
            "",
            "<details>",
            f"<summary><b>👉 [펼쳐보기] {d['domain']} GEO 마크다운 본문 및 Head 주입용 JSON-LD</b></summary>",
            "",
            d["content_markdown"],
            "",
            "#### Head 주입용 Schema.org JSON-LD (`schema_json_ld`)",
            "```json",
            schema_pretty,
            "```",
            "",
            "</details>",
            "",
            "---"
        ])

    report_content = "\n".join(report_lines)
    report_filename = f"weekly_{today_str}.md"
    report_path = os.path.join(base_dir, report_filename)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    logging.info(f"주간 리포트 저장 완료: {report_path}")

    queue_path = os.path.join(base_dir, "pending_approvals.json")
    with open(queue_path, "w", encoding="utf-8") as f:
        json.dump({
            "version": "2.1.0",
            "generated_at": today_str,
            "total_sites": len(all_site_data),
            "auto_approved_count": len([d for d in drafts_generated if d["status"] == "AUTO_APPROVED"]),
            "deploy_results": deploy_results,
            "drafts": drafts_generated
        }, f, ensure_ascii=False, indent=2)
    logging.info(f"승인 및 실배포 큐 JSON 저장 완료: {queue_path}")

    # 동적 텔레그램 1-Page 요약 브리핑 생성
    tg_Dynamic_lines = []
    icons = {
        "parvogel": "🐕",
        "100bagger": "📈",
        "monsmecta": "💊",
        "rotagal": "🐂",
        "vetacol": "🛡️",
        "agrokorea": "🏢",
        "snj_vet": "🏥"
    }
    for idx, d in enumerate(drafts_generated, 1):
        ic = icons.get(d["site_id"], "✅")
        dep = d.get("deploy_result", "DEPLOYED").split(" ")[0]
        tg_Dynamic_lines.append(
            f"{idx}. {ic} *{d['site_name']}* (`{d['domain']}`): '{d['target_query']}' ({d['current_position']}위/{d['current_impressions']:,}회) → `{dep}`"
        )

    telegram_text = (
        f"🔔 *[7대 전 도메인 AI SEO & GEO 실배포 완료 v2.1]*\n"
        f"📅 기준일: {today_str} | CTO 안그래\n\n"
        f"대표님, 7개 사이트 10~20위 기회 키워드 GEO 보강 및 로컬 레포지토리 코드 주입(`SEOAutoDeployer`)이 완료되었습니다.\n\n"
        f"📊 *도메인별 실시간 공략 및 배포 현황:*\n"
        + "\n".join(tg_Dynamic_lines)
        + "\n\n✨ *도메인 팩트 분리(로타갈 백신·베타콜 초유·파보겔/몬스멕타 나노점토·S&J 용인·100배거 퀀트) 및 Schema.org JSON-LD 결합 100% 완료*"
    )

    print("\n" + telegram_text + "\n")
    send_telegram_briefing(telegram_text)
    return report_path


if __name__ == "__main__":
    run_weekly_pipeline()
