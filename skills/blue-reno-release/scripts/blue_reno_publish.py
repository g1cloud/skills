#!/usr/bin/env python3
"""Blue Reno Open API로 릴리즈 노트를 업서트(없으면 생성 / 있으면 수정)하고 게시한다.

API 키는 BLUERENO_API_KEY 환경변수로만 읽는다. 명령행 인자로 받지 않는 이유는
명령행이 터미널 기록·프로세스 목록·로그에 그대로 남기 때문이다.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import NoReturn


def fail(message) -> NoReturn:
    print(f"오류: {message}", file=sys.stderr)
    sys.exit(1)


DEFAULT_URL = "https://bluereno.g1project.net"


def normalize_base(url):
    """BLUERENO_URL이 오리진이든 /api/v1까지 포함하든 동일하게 동작시킨다."""
    base = url.strip().rstrip("/")
    if base.endswith("/api/v1"):
        base = base[: -len("/api/v1")]
    return f"{base}/api/v1"


def api(base, key, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(f"{base}{path}", data=data, method=method)
    request.add_header("Authorization", f"Bearer {key}")
    if data is not None:
        request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as error:
        raw = error.read().decode(errors="replace")
        try:
            detail = json.loads(raw).get("statusMessage") or raw
        except json.JSONDecodeError:
            detail = raw
        if error.code == 401:
            fail("API 키가 유효하지 않다 (401). BLUERENO_API_KEY를 확인할 것.")
        if error.code == 404:
            # 서버는 정보 노출을 막으려고 권한 부족도 404로 응답한다.
            # 둘 중 무엇인지는 --list-artifacts로 가려낼 수 있다.
            fail(
                f"대상이 없거나 Editor 권한이 없다 (404). {method} {path}\n"
                "       --list-artifacts 로 접근 가능한 Artifact와 내 권한을 확인할 것."
            )
        fail(f"{method} {path} → HTTP {error.code}: {detail}")
    except urllib.error.URLError as error:
        fail(f"{base} 접속 실패: {error.reason}")


def find_by_version(base, key, artifact_id, version):
    """목록 API에 버전 필터가 없어서 전체를 훑으며 직접 매칭한다."""
    matches = []
    page = 1
    while True:
        result = api(base, key, "GET", f"/artifacts/{artifact_id}/release-notes?page={page}&limit=100")
        notes = result.get("data") or []
        matches += [note for note in notes if note.get("version") == version]
        total_pages = (result.get("pagination") or {}).get("totalPages") or 1
        if not notes or page >= total_pages:
            return matches
        page += 1


WRITABLE_ROLES = ("owner", "editor")


def list_artifacts(base, key):
    """접근 가능한 Artifact를 Organization / Product 경로와 함께 출력한다."""
    data = api(base, key, "GET", "/entities")["data"]
    org_name = {org["id"]: org["name"] for org in data["organizations"]}
    products = {product["id"]: product for product in data["products"]}
    artifacts = data["artifacts"]

    if not artifacts:
        print("접근 가능한 Artifact가 없다. 웹에서 멤버로 등록됐는지 확인할 것.")
        return

    groups = {}
    for artifact in artifacts:
        product = products.get(artifact["productId"], {})
        path = f"{org_name.get(product.get('organizationId'), '?')} / {product.get('name', '?')}"
        groups.setdefault(path, []).append(artifact)

    width = max(len(artifact["name"]) for artifact in artifacts)
    print("접근 가능한 Artifact  (✎ = 릴리즈 노트를 올릴 수 있음)\n")
    for path in sorted(groups):
        print(path)
        for artifact in groups[path]:
            role = artifact.get("role") or "-"
            mark = "✎" if role in WRITABLE_ROLES else " "
            print(f"  {mark} {artifact['id']:>4}  {artifact['name']:<{width}}  {role}")
    print("\n원하는 id를 --artifact-id 로 넘기거나 BLUERENO_ARTIFACT_ID 에 설정할 것.")


def main():
    parser = argparse.ArgumentParser(description="Blue Reno 릴리즈 노트 업서트 + 게시")
    parser.add_argument("--version", help="버전 표기 (예: 2.4.0, v 접두사 없음)")
    parser.add_argument("--content-file", help="본문 Markdown 파일 경로")
    parser.add_argument("--artifact-id", help="대상 Artifact ID (기본값: BLUERENO_ARTIFACT_ID)")
    parser.add_argument(
        "--list-artifacts",
        action="store_true",
        help="접근 가능한 Organization / Product / Artifact와 권한을 출력하고 종료",
    )
    parser.add_argument("--tags", help="변경 유형 태그 쉼표 구분 (예: feat,fix,breaking). 미지정 시 기존 값 유지")
    parser.add_argument("--released-at", help="릴리즈 일시 ISO 8601. 미지정 시 기존 값 유지, 없으면 현재 시각")
    parser.add_argument("--draft", action="store_true", help="게시하지 않고 draft로 둔다")
    parser.add_argument("--dry-run", action="store_true", help="아무것도 바꾸지 않고 수행할 동작만 출력")
    args = parser.parse_args()

    url = os.environ.get("BLUERENO_URL") or DEFAULT_URL
    key = os.environ.get("BLUERENO_API_KEY")
    artifact_id = args.artifact_id or os.environ.get("BLUERENO_ARTIFACT_ID")

    if not key:
        # 키는 사용자만 발급받을 수 있다. 대체 경로가 없으므로 여기서 멈춘다.
        fail("BLUERENO_API_KEY가 비어 있다. .claude/settings.local.json 에 넣고 Claude Code를 재시작할 것.")
    # 탐색 모드는 아직 대상을 모르는 상태에서 쓰므로 Artifact ID를 요구하지 않는다.
    if not args.list_artifacts and not artifact_id:
        fail("BLUERENO_ARTIFACT_ID가 비어 있다. --list-artifacts 로 대상을 먼저 확인할 것.")

    base = normalize_base(url)
    if args.list_artifacts:
        print(f"서버: {url}\n")
        list_artifacts(base, key)
        return

    for name, value in (("--version", args.version), ("--content-file", args.content_file)):
        if not value:
            fail(f"{name} 이(가) 필요하다.")

    try:
        content = open(args.content_file, encoding="utf-8").read()
    except OSError as error:
        fail(f"본문 파일을 읽을 수 없다: {error}")
    if not content.strip():
        fail("본문이 비어 있다.")

    version = args.version.strip()
    # 서버가 소문자화·별칭 정리·중복 제거를 하므로 여기서는 쪼개기만 한다.
    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()] if args.tags else None
    publish = not args.draft
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    matches = find_by_version(base, key, artifact_id, version)
    if len(matches) > 1:
        ids = ", ".join(str(note["id"]) for note in matches)
        fail(f"버전 '{version}' 노트가 {len(matches)}건 있다 (id: {ids}). 어느 것을 고칠지 알 수 없으니 웹에서 정리한 뒤 다시 실행할 것.")
    existing = matches[0] if matches else None

    if existing:
        payload = {"content": content}
        if tags is not None:
            payload["tags"] = tags
        if args.released_at:
            payload["releasedAt"] = args.released_at
        elif publish and not existing.get("releasedAt"):
            # 게시하려면 릴리즈 일시가 있어야 한다. 기존 값이 있으면 건드리지 않는다.
            payload["releasedAt"] = now
        action = f"기존 노트 수정 (id={existing['id']}, 현재 상태={existing['status']})"
    else:
        payload = {"version": version, "content": content}
        if tags is not None:
            payload["tags"] = tags
        if args.released_at:
            payload["releasedAt"] = args.released_at
        elif publish:
            payload["releasedAt"] = now
        action = "신규 노트 생성"

    if args.dry_run:
        print(f"[dry-run] 대상: {url} / artifact {artifact_id} / 버전 {version}")
        print(f"[dry-run] 동작: {action}")
        print(f"[dry-run] tags     : {', '.join(tags) if tags else '기존 값 유지'}")
        print(f"[dry-run] releasedAt: {payload.get('releasedAt', '기존 값 유지')}")
        print(f"[dry-run] 게시 여부: {'published로 전환' if publish else 'draft 유지'}")
        print(f"[dry-run] 본문 {len(content)}자")
        return

    if existing:
        note = api(base, key, "PATCH", f"/release-notes/{existing['id']}", payload)["data"]
    else:
        note = api(base, key, "POST", f"/artifacts/{artifact_id}/release-notes", payload)["data"]

    if publish and note.get("status") != "published":
        note = api(base, key, "PATCH", f"/release-notes/{note['id']}/status", {"status": "published"})["data"]

    print(f"완료: {action.split(' (')[0]}")
    print(f"  id        : {note['id']}")
    print(f"  version   : {note['version']}")
    print(f"  status    : {note['status']}")
    print(f"  releasedAt: {note.get('releasedAt')}")


if __name__ == "__main__":
    main()
