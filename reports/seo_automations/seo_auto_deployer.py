#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
seo_auto_deployer.py (v2.1 End-to-End 7-Site Auto-Deployer Engine)
`pending_approvals.json`에서 AUTO_APPROVED 판정을 받은 GEO 초안 및 Schema.org JSON-LD를
실제 7개 홈페이지의 로컬 레포지토리에 자동 주입(Inject)하고 프리렌더러를 구동하는 실행 엔진.
"""

import os
import re
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class SEOAutoDeployer:
    def __init__(self, config_path: str = "sites_config.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.isabs(config_path):
            config_path = os.path.join(base_dir, config_path)
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.sites_by_id = {s["id"]: s for s in self.config.get("sites", [])}

    def deploy_approved_drafts(self, drafts: List[Dict[str, Any]]) -> Dict[str, str]:
        """AUTO_APPROVED 상태인 초안들을 각 사이트 어댑터로 실제 배포합니다."""
        deploy_results: Dict[str, str] = {}
        today_str = datetime.now().strftime("%Y-%m-%d")

        for draft in drafts:
            sid = draft.get("site_id")
            if draft.get("status") != "AUTO_APPROVED":
                deploy_results[sid] = "SKIPPED_MANUAL_REVIEW"
                continue

            site = self.sites_by_id.get(sid)
            if not site:
                deploy_results[sid] = "ERROR_SITE_NOT_FOUND"
                continue

            repo_path = site.get("local_repo_path", "")
            if not repo_path or not os.path.exists(repo_path):
                deploy_results[sid] = f"SKIPPED_REPO_MISSING ({repo_path})"
                continue

            adapter_type = site.get("deploy_adapter", "static_html_schema")
            try:
                if adapter_type == "json_blog_prerender":
                    res = self._deploy_json_blog_prerender(site, draft, today_str)
                elif adapter_type == "quant_seo_feed":
                    res = self._deploy_quant_seo_feed(site, draft, today_str)
                else:
                    res = self._deploy_static_html_schema(site, draft, today_str)

                draft["deployed_at"] = datetime.now().isoformat()
                draft["deploy_result"] = res
                deploy_results[sid] = res
            except Exception as e:
                logging.error(f"[{sid}] Auto-deploy error: {e}")
                deploy_results[sid] = f"ERROR: {e}"

        return deploy_results

    def _deploy_json_blog_prerender(self, site: Dict[str, Any], draft: Dict[str, Any], today_str: str) -> str:
        """
        Type A (파보겔 등 Vite React + posts.json 프리렌더 구조):
        1. `src/data/posts.json`의 타겟 블로그 포스트에 최신 GEO 섹션 및 `schema_json_ld`, `dateModified` 병합
        2. `dist/`가 존재할 경우 `node scripts/prerender_blogs.js` 즉시 실행하여 정적 HTML 재생성
        """
        repo_path = site["local_repo_path"]
        target_cfg = site.get("content_target", {})
        posts_rel = target_cfg.get("posts_json_path", "src/data/posts.json")
        posts_path = os.path.join(repo_path, posts_rel)

        if not os.path.exists(posts_path):
            return "SKIPPED_NO_POSTS_JSON"

        with open(posts_path, "r", encoding="utf-8") as f:
            posts = json.load(f)

        target_url = draft.get("target_url", "")
        slug = target_url.rstrip("/").split("/")[-1] if "/blog/" in target_url else ""

        matched_post = None
        for p in posts:
            if p.get("id") == slug:
                matched_post = p
                break
        if not matched_post and posts:
            matched_post = posts[0]

        if matched_post:
            marker = "<!-- GEO_AUTO_BOOST_START -->"
            end_marker = "<!-- GEO_AUTO_BOOST_END -->"
            clean_md = draft["content_markdown"]
            geo_block = f"\n\n---\n\n{marker}\n{clean_md}\n{end_marker}"

            existing_content = matched_post.get("content", "")
            # 기존에 잘못 주입되었을 수 있는 코드블록 JSON-LD 제거
            existing_content = re.sub(r"<!--\s*Schema\.org\s*JSON-LD\s*-->[\s\S]*?```json[\s\S]*?```", "", existing_content)

            if marker in existing_content and end_marker in existing_content:
                pattern = re.compile(f"{re.escape(marker)}[\\s\\S]*?{re.escape(end_marker)}")
                matched_post["content"] = pattern.sub(f"{marker}\n{clean_md}\n{end_marker}", existing_content).strip()
            else:
                matched_post["content"] = (existing_content.strip() + geo_block).strip()

            matched_post["dateModified"] = today_str
            matched_post["schema_json_ld"] = draft.get("schema_json_ld")

            with open(posts_path, "w", encoding="utf-8") as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)

            # 프리렌더러 실행 (dist 폴더가 있을 때 즉시 반영)
            prerender_rel = target_cfg.get("prerender_script", "scripts/prerender_blogs.js")
            prerender_path = os.path.join(repo_path, prerender_rel)
            dist_dir = os.path.join(repo_path, "dist")
            if os.path.exists(prerender_path) and os.path.exists(dist_dir):
                subprocess.run(["node", prerender_path], cwd=repo_path, capture_output=True, text=True, timeout=30)
                return f"DEPLOYED_AND_PRERENDERED ({matched_post.get('id')})"

            return f"DEPLOYED_POSTS_JSON ({matched_post.get('id')})"

        return "NO_MATCHING_POST"

    def _deploy_static_html_schema(self, site: Dict[str, Any], draft: Dict[str, Any], today_str: str) -> str:
        """
        Type B (몬스멕타, 로타갈, 베타콜, 한국아그로, S&J동물병원):
        1. `geo_insights.json`에 최신 GEO 마크다운, JSON-LD, 숏폼/커뮤니티 파생 원고 저장
        2. `index.html`에 `<script id="geo-weekly-ld" type="application/ld+json">` 동적 스키마 자동 주입/갱신
        """
        repo_path = site["local_repo_path"]
        target_cfg = site.get("content_target", {})
        geo_json_rel = target_cfg.get("geo_json_path", "geo_insights.json")
        geo_json_path = os.path.join(repo_path, geo_json_rel)

        os.makedirs(os.path.dirname(geo_json_path), exist_ok=True)
        payload = {
            "updated_at": today_str,
            "site_id": site["id"],
            "domain": site["domain"],
            "target_query": draft.get("target_query"),
            "target_url": draft.get("target_url"),
            "section_title": draft.get("section_title"),
            "content_markdown": draft.get("content_markdown"),
            "schema_json_ld": draft.get("schema_json_ld"),
            "sns_derivatives": draft.get("sns_derivatives", {})
        }
        with open(geo_json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        index_rel = target_cfg.get("index_html_path", "index.html")
        index_path = os.path.join(repo_path, index_rel)
        if os.path.exists(index_path) and draft.get("schema_json_ld"):
            with open(index_path, "r", encoding="utf-8") as f:
                html = f.read()

            schema_str = json.dumps(draft["schema_json_ld"], ensure_ascii=False, indent=2)
            script_block = f'<script id="geo-weekly-ld" type="application/ld+json">\n{schema_str}\n</script>'

            if 'id="geo-weekly-ld"' in html:
                html = re.sub(
                    r'<script id="geo-weekly-ld" type="application/ld\+json">[\s\S]*?</script>',
                    lambda _: script_block,
                    html,
                    count=1
                )
            elif "</head>" in html:
                html = html.replace("</head>", f"  {script_block}\n</head>", 1)

            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html)

            return f"DEPLOYED_HTML_AND_GEO_JSON ({index_rel})"

        return f"DEPLOYED_GEO_JSON ({geo_json_rel})"

    def _deploy_quant_seo_feed(self, site: Dict[str, Any], draft: Dict[str, Any], today_str: str) -> str:
        """
        Type C (100-Bagger 퀀트 시스템):
        `quant_system/reports/seo_quant_insights.json` 및 `100_bagger_saas/public/geo_quant_insights.json`에 동시 배포
        """
        repo_path = site["local_repo_path"]
        target_cfg = site.get("content_target", {})
        feed_rel = target_cfg.get("seo_feed_path", "reports/seo_quant_insights.json")
        feed_path = os.path.join(repo_path, feed_rel)
        os.makedirs(os.path.dirname(feed_path), exist_ok=True)

        payload = {
            "updated_at": today_str,
            "domain": site["domain"],
            "target_query": draft.get("target_query"),
            "content_markdown": draft.get("content_markdown"),
            "schema_json_ld": draft.get("schema_json_ld"),
            "sns_derivatives": draft.get("sns_derivatives", {})
        }
        with open(feed_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        saas_public = os.path.join(repo_path, "100_bagger_saas", "public")
        if os.path.exists(saas_public):
            saas_feed = os.path.join(saas_public, "geo_quant_insights.json")
            with open(saas_feed, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            return "DEPLOYED_QUANT_SAAS_AND_FEED"

        return f"DEPLOYED_QUANT_FEED ({feed_rel})"
