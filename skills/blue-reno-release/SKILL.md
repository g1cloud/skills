---
name: blue-reno-release
description: Blue Reno(BlueReNo) 릴리즈 노트 플랫폼에 Open API로 릴리즈 노트를 등록·수정·게시한다. 같은 버전이 이미 있으면 수정, 없으면 생성한 뒤 published까지 전환한다. 사용자가 "릴리즈 노트 올려줘", "이번 버전 릴리즈 노트 작성해서 게시", "Blue Reno에 등록/배포", "릴리즈 노트 퍼블리시"처럼 말하거나, 버전 태그를 자르면서 릴리즈 노트를 남기려 할 때는 반드시 이 스킬을 사용할 것. 본문을 직접 주지 않아도 git 로그에서 초안을 만들어 확인받은 뒤 올린다.
---

# Blue Reno 릴리즈 노트 게시

Blue Reno의 Open API(`/api/v1`)로 릴리즈 노트를 올린다. 업로드 자체는
`scripts/blue_reno_publish.py`가 전담한다. 이 스킬이 직접 `curl`을 조립하지 않는 이유는,
마크다운 본문에 개행·따옴표·백틱이 섞이면 셸에서 JSON을 만들다 깨지기 쉽고,
목록 API에 버전 필터가 없어 페이지네이션을 직접 훑어야 하며, API 키가 명령행에 남으면 안 되기 때문이다.

## 사전 조건

스크립트는 설정을 **환경변수로만** 읽는다. Claude Code는 `.claude/settings.json`의 `env` 블록을
Bash 실행 환경에 주입하므로, 설정은 그 파일에 넣는다.

| 환경변수 | 위치 | 필수 | 값 |
|---|---|---|---|
| `BLUERENO_API_KEY` | **`.claude/settings.local.json`** | ✅ | `brn_...` (커밋 금지) |
| `BLUERENO_URL` | `.claude/settings.json` | — | 오리진만. **미설정 시 `https://bluereno.g1project.net`** |
| `BLUERENO_ARTIFACT_ID` | `.claude/settings.json` | — | `6`. 없으면 아래 "Artifact ID를 모를 때" 참조 |

```json
{ "env": { "BLUERENO_URL": "https://bluereno.g1project.net", "BLUERENO_ARTIFACT_ID": "6" } }
```

URL은 기본값이 있으니 자체 호스팅 인스턴스를 쓸 때만 지정하면 된다.
값을 출력하거나 명령행에 직접 쓰지 말 것 — 키가 셸 히스토리와 프로세스 목록에 남는다.

### 키가 없으면 (BLUERENO_API_KEY 미설정)

키 평문은 사용자만 얻을 수 있다. 에이전트가 대신 발급할 방법이 없으므로 **여기서 작업을 멈추고
플레이스홀더를 만든 뒤 사용자에게 넘긴다.** 게시를 계속 시도하지 말 것.

`.claude/settings.local.json`을 만든다. 이미 있으면 **기존 내용을 보존하고 `env` 키만 병합**한다.

```json
{ "env": { "BLUERENO_API_KEY": "brn_여기에_발급받은_키를_붙여넣으세요" } }
```

그리고 사용자에게 이렇게 안내한다.

1. Blue Reno에 로그인 → 좌측 하단 프로필 메뉴 → **"API 키"** → 새 키 발급
2. 평문은 **발급 직후 한 번만** 보이므로 그 자리에서 복사
3. `.claude/settings.local.json`의 플레이스홀더를 실제 키로 교체
4. **Claude Code 재시작** — `env` 주입은 세션 시작 시점에만 일어난다

`.claude/settings.local.json`은 `.gitignore`에 등록돼 있어 커밋되지 않는다. 키를
`.claude/settings.json`(커밋 대상)에 넣지 말 것. 키 소유자가 대상 Artifact에 **Editor 이상**이어야 한다.

### Artifact ID를 모를 때

`BLUERENO_ARTIFACT_ID`가 설정돼 있지 않거나 어디에 올릴지 불확실하면 먼저 조회한다.
이 모드는 키만 있으면 되고, 아무것도 바꾸지 않는다.

```bash
python3 .claude/skills/blue-reno-release/scripts/blue_reno_publish.py --list-artifacts
```

```text
서버: https://bluereno.g1project.net

접근 가능한 Artifact  (✎ = 릴리즈 노트를 올릴 수 있음)

Kimos / BlueReno
  ✎    6  bluereno   owner
UZEN / G1 commerce cloud
       1  System     viewer
```

`✎`가 붙은 것만 게시 대상이 될 수 있다(owner/editor). **여러 개면 임의로 고르지 말고 사용자에게 확인받는다** —
엉뚱한 제품에 올리면 외부에 바로 공개된다. 확정된 id는 `--artifact-id`로 넘기고, 앞으로도 계속 쓸
저장소라면 `.claude/settings.json`의 `BLUERENO_ARTIFACT_ID`에 넣어두라고 안내한다.

## 워크플로

### 1. 버전 확정

인자로 받았으면 그대로 쓴다. 없으면 후보를 찾아 사용자에게 확인받는다.

```bash
git describe --tags --abbrev=0 2>/dev/null   # 직전 태그
```

Blue Reno의 표기 규칙은 `v` 접두사 없는 `2.4.0` 형식이다. 태그가 `v2.4.0`이면 `v`를 떼고 쓴다.

### 2. 본문 확보

파일 경로나 본문을 받았으면 그것을 쓴다. 없으면 직전 태그 이후 커밋에서 초안을 만든다.

```bash
git log --no-merges --pretty='- %s' <직전태그>..HEAD
```

커밋 제목을 그대로 나열하지 말 것. 릴리즈 노트를 읽는 사람은 그 리포에서 무슨 일이 있었는지가 아니라
**자기한테 뭐가 달라지는지**를 알고 싶어 한다. 사용자 관점으로 묶고, 내부 리팩터링·CI 설정처럼
바깥에서 체감되지 않는 변경은 생략하거나 한 줄로 합친다. 한국어로 쓴다.

```markdown
### 새 기능
- 릴리즈 노트를 API로 등록할 수 있습니다.

### 개선
- 사이드바에서 상속된 권한의 하위 항목도 표시됩니다.

### 버그 수정
- 멤버 관리 화면이 간헐적으로 404를 반환하던 문제를 수정했습니다.
```

초안을 임시 파일(스크래치패드 디렉터리가 있으면 거기, 없으면 `mktemp`)에 저장하고,
**사용자에게 본문을 보여준 뒤 동의를 받는다.** 게시되면 외부에 바로 공개되므로 되돌리기 번거롭다.

### 3. 태그 결정

목록·타임라인 화면의 배지는 본문을 파싱하지 않고 **태그 값만** 쓴다. 태그가 비면 배지가 아예 안 나오므로
이 릴리즈에 실제로 담긴 변경 유형을 골라 넣는다. 커밋 프리픽스(`feat:`, `fix:` 등)가 좋은 출처다.

권장 태그: `feat` / `fix` / `breaking` / `mig` / `perf` / `docs` / `refactor` / `chore`.
노트당 최대 8개이며, 서버가 소문자화·별칭 정리(`feature`→`feat`, `bugfix`→`fix`)·중복 제거를 한다.
`breaking`은 빨강으로 강조되므로 실제 호환성이 깨질 때만 붙인다.

### 4. 신규인지 수정인지 먼저 보여준다

```bash
python3 .claude/skills/blue-reno-release/scripts/blue_reno_publish.py \
  --version 2.4.0 --content-file /tmp/note.md --tags feat,fix --dry-run
```

"신규 생성"인지 "기존 노트 수정(현재 상태 draft/published)"인지, 그리고 **어느 서버에 올라가는지**
출력된다. 출력된 서버 주소가 의도한 곳인지 확인할 것.
**이미 published인 노트를 덮어쓰는 경우라면 실행 전에 반드시 사용자에게 알린다** —
이미 공개된 내용을 바꾸는 일이라 사용자가 의도한 게 맞는지 확인이 필요하다.

### 5. 실행

```bash
python3 .claude/skills/blue-reno-release/scripts/blue_reno_publish.py \
  --version 2.4.0 --content-file /tmp/note.md --tags feat,fix
```

기본 동작은 게시까지다: 없으면 POST로 생성, 있으면 PATCH로 수정한 뒤 `published`로 전환한다.
게시에는 릴리즈 일시가 필수라 비어 있으면 현재 시각으로 채우고, 기존 값이 있으면 보존한다.

| 옵션 | 용도 |
|---|---|
| `--tags feat,fix` | 변경 유형 태그. 생략하면 기존 노트의 태그를 그대로 둔다 |
| `--artifact-id N` | 환경변수 기본값 대신 다른 Artifact에 올릴 때 |
| `--list-artifacts` | 접근 가능한 Artifact와 내 권한만 출력하고 종료 |
| `--released-at 2026-06-10T09:00:00Z` | 릴리즈 일시를 명시할 때 (기존 값도 덮어쓴다) |
| `--draft` | 게시하지 않고 초안으로만 둘 때 |

### 6. 보고

노트 id / 버전 / 상태 / 릴리즈 일시를 그대로 전달한다. 임시 본문 파일은 지운다.

## 실패했을 때

| 증상 | 원인과 대응 |
|---|---|
| `401` | API 키가 없거나 무효. `BLUERENO_API_KEY`를 확인하고, 키가 삭제됐으면 재발급받게 안내한다. |
| `404` | 서버가 권한 부족도 404로 응답하므로 "없음"과 "권한 없음"이 구분되지 않는다. `--list-artifacts`로 가려낼 것 — 목록에 그 id가 없으면 존재하지 않거나 아예 접근 권한이 없는 것이고, `✎` 없이 `viewer`로 나오면 읽기만 되는 상태다. |
| `게시하려면 릴리즈 일시를 설정해 주세요` | `--released-at`을 명시해 다시 실행한다. |
| `버전 '...' 노트가 N건 있다` | 서버가 버전 중복을 막지 않아 같은 버전이 여러 개 생길 수 있다. 어느 것을 고칠지 추측하지 말고 웹에서 정리하도록 안내한다. |
