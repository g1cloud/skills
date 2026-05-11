#!/usr/bin/env bash
# Statusline inspired by oh-my-claudecode HUD design
# https://github.com/Yeachan-Heo/oh-my-claudecode (src/hud/)
#
# Reads Claude Code statusline JSON from stdin and prints a single-line HUD:
#   Model | ~/cwd | repo:NAME | branch:BR | +S !M ?U ⇡A ⇣B | ctx:[..]NN% | 5h:NN%(Hh Mm) wk:NN%(Dd Hh)

set -u
export LC_ALL=${LC_ALL:-en_US.UTF-8}

input=$(cat)

# --- Parse all fields with one jq call (line-delimited; empty values preserved) ---
fields=()
while IFS= read -r line; do
    fields+=("$line")
done < <(printf '%s' "$input" | jq -r '
  def reset2epoch:
    if . == null or . == "" then ""
    elif type == "number" then (. | tostring)
    else (fromdate | tostring)
    end;
  [
    (.model.id // ""),
    (.model.display_name // ""),
    (.workspace.current_dir // .cwd // ""),
    (.context_window.used_percentage // ""  | tostring),
    (.rate_limits.five_hour.used_percentage // "" | tostring),
    (.rate_limits.five_hour.resets_at // "" | reset2epoch),
    (.rate_limits.seven_day.used_percentage // "" | tostring),
    (.rate_limits.seven_day.resets_at // "" | reset2epoch)
  ] | .[]
' 2>/dev/null)

model_id="${fields[0]:-}"
model_display="${fields[1]:-}"
cwd="${fields[2]:-}"
ctx_pct="${fields[3]:-}"
fh_pct="${fields[4]:-}"
fh_reset="${fields[5]:-}"
wk_pct="${fields[6]:-}"
wk_reset="${fields[7]:-}"

# --- ANSI ---
R=$'\e[0m'; D=$'\e[2m'
RED=$'\e[31m'; GRN=$'\e[32m'; YLW=$'\e[33m'; CYN=$'\e[36m'; MAG=$'\e[35m'
SEP="${D} | ${R}"

join_parts() {
    local out=""
    for p in "$@"; do
        [ -z "$p" ] && continue
        if [ -z "$out" ]; then out="$p"; else out="${out}${SEP}${p}"; fi
    done
    printf '%s' "$out"
}

# --- Helpers ---
to_int() {
    local v="$1"
    [ -z "$v" ] || [ "$v" = "null" ] && { echo ""; return; }
    printf '%.0f' "$v" 2>/dev/null || echo ""
}

clamp_pct() {
    local v="$1"
    [ "$v" -lt 0 ] 2>/dev/null && v=0
    [ "$v" -gt 100 ] 2>/dev/null && v=100
    echo "$v"
}

rate_color() {  # 70/90 threshold
    local p="$1"
    if   [ "$p" -ge 90 ]; then printf '%s' "$RED"
    elif [ "$p" -ge 70 ]; then printf '%s' "$YLW"
    else                       printf '%s' "$GRN"
    fi
}

ctx_color() {  # 70/85 threshold
    local p="$1"
    if   [ "$p" -ge 85 ]; then printf '%s' "$RED"
    elif [ "$p" -ge 70 ]; then printf '%s' "$YLW"
    else                       printf '%s' "$GRN"
    fi
}

# Human-readable duration until epoch timestamp
fmt_reset() {
    local epoch="$1"
    [ -z "$epoch" ] || [ "$epoch" = "null" ] && return
    local now; now=$(date +%s)
    local diff=$((epoch - now))
    [ $diff -le 0 ] && return
    local mins=$((diff / 60))
    local hours=$((mins / 60))
    local days=$((hours / 24))
    if [ $days -gt 0 ]; then
        printf '%dd%dh' "$days" "$((hours % 24))"
    else
        printf '%dh%dm' "$hours" "$((mins % 60))"
    fi
}

# --- Model: tier color + versioned name ---
model_src="${model_id:-$model_display}"
model_lc=$(printf '%s' "$model_src" | tr '[:upper:]' '[:lower:]')
m_name=""; m_color="$CYN"; m_ver=""
case "$model_lc" in
    *opus*)   m_name="Opus";   m_color="$MAG" ;;
    *sonnet*) m_name="Sonnet"; m_color="$YLW" ;;
    *haiku*)  m_name="Haiku";  m_color="$GRN" ;;
    *)        m_name="${model_display:-$model_id}" ;;
esac
if [[ "$model_lc" =~ (opus|sonnet|haiku)-([0-9]+)-([0-9]+) ]]; then
    m_ver=" ${BASH_REMATCH[2]}.${BASH_REMATCH[3]}"
fi
model_el=""
[ -n "$m_name" ] && model_el="${m_color}${m_name}${m_ver}${R}"

# --- CWD ---
cwd_el=""
if [ -n "$cwd" ]; then
    if [ "$cwd" = "$HOME" ]; then
        disp="~"
    elif [ "$cwd" = "/" ]; then
        disp="/"
    else
        disp="${cwd##*/}"
    fi
    cwd_el="${D}${disp}${R}"
fi

# --- Git ---
git_el=""
if [ -n "$cwd" ] && [ -d "$cwd" ] && git -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    branch=$(git -C "$cwd" branch --show-current 2>/dev/null)
    if [ -n "$branch" ]; then
        br_el="${D}branch:${R}${CYN}${branch}${R}"

        gd=$(git -C "$cwd" rev-parse --git-dir 2>/dev/null)
        cd_=$(git -C "$cwd" rev-parse --git-common-dir 2>/dev/null)
        if [ -n "$gd" ] && [ -n "$cd_" ] && [ "$gd" != "$cd_" ]; then
            br_el="${br_el} ${D}(wt:${R}${CYN}${gd##*/}${D})${R}"
        fi

        st_el=""
        status=$(git -C "$cwd" --no-optional-locks status --porcelain -b 2>/dev/null || true)
        if [ -n "$status" ]; then
            staged=0; modified=0; untracked=0; ahead=0; behind=0
            line_no=0
            while IFS= read -r line; do
                line_no=$((line_no+1))
                if [ $line_no -eq 1 ]; then
                    [[ "$line" =~ ahead\ ([0-9]+) ]] && ahead="${BASH_REMATCH[1]}"
                    [[ "$line" =~ behind\ ([0-9]+) ]] && behind="${BASH_REMATCH[1]}"
                    continue
                fi
                [ ${#line} -lt 2 ] && continue
                idx="${line:0:1}"; wt="${line:1:1}"
                if [ "$idx" = "?" ]; then
                    untracked=$((untracked+1))
                else
                    [ "$idx" != " " ] && staged=$((staged+1))
                    { [ "$wt" = "M" ] || [ "$wt" = "D" ]; } && modified=$((modified+1))
                fi
            done <<< "$status"

            sp=""
            [ $staged    -gt 0 ] && sp="${GRN}+${R}${staged}"
            [ $modified  -gt 0 ] && sp="${sp:+$sp }${RED}!${R}${modified}"
            [ $untracked -gt 0 ] && sp="${sp:+$sp }${CYN}?${R}${untracked}"
            [ $ahead     -gt 0 ] && sp="${sp:+$sp }${GRN}⇡${R}${ahead}"
            [ $behind    -gt 0 ] && sp="${sp:+$sp }${RED}⇣${R}${behind}"
            st_el="$sp"
        fi

        git_el=$(join_parts "$br_el" "$st_el")
    fi
fi

# --- Context ---
ctx_el=""
ctx_int=$(to_int "$ctx_pct")
if [ -n "$ctx_int" ]; then
    pct=$(clamp_pct "$ctx_int")
    c=$(ctx_color "$pct")
    sfx=""
    [ "$pct" -ge 85 ] && sfx=" CRITICAL"
    ctx_el="${D}ctx:${R}${c}${pct}%${sfx}${R}"
fi

# --- Rate limits: 5h + wk ---
fh_el=""
fh_int=$(to_int "$fh_pct")
if [ -n "$fh_int" ]; then
    p=$(clamp_pct "$fh_int")
    c=$(rate_color "$p")
    reset=$(fmt_reset "$fh_reset")
    if [ -n "$reset" ]; then
        fh_el="${D}5h:${R}${c}${p}%${R}${D}(${reset})${R}"
    else
        fh_el="${D}5h:${R}${c}${p}%${R}"
    fi
fi

wk_el=""
wk_int=$(to_int "$wk_pct")
if [ -n "$wk_int" ]; then
    p=$(clamp_pct "$wk_int")
    c=$(rate_color "$p")
    reset=$(fmt_reset "$wk_reset")
    if [ -n "$reset" ]; then
        wk_el="${D}wk:${R}${c}${p}%${R}${D}(${reset})${R}"
    else
        wk_el="${D}wk:${R}${c}${p}%${R}"
    fi
fi

join_parts "$model_el" "$fh_el" "$wk_el" "$ctx_el" "$cwd_el" "$git_el"
