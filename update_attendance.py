#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
13개 학생 페이지에 출석 현황 + 날짜별 피드백 섹션 추가
"""

import re

BASE_DIR = r"C:\Users\Admin\Desktop\Claude\github-deploy\sbs-school-proposal\student"

DATES = [
    ("03-17", "월"),
    ("03-19", "수"),
    ("03-24", "월"),
    ("03-26", "수"),
    ("03-31", "월"),
    ("04-02", "수"),
]

# 학생별 출석 데이터 (O=출석, X=결석, -=해당없음)
ATTENDANCE = {
    "kim-geonwoo":  ["O", "O", "X", "O", "O", "O"],
    "kim-sumin":    ["O", "O", "O", "O", "O", "O"],
    "kim-siwoo":    ["O", "O", "O", "O", "X", "X"],
    "nam-jaeseo":   ["O", "O", "O", "O", "O", "O"],
    "noh-wontae":   ["-", "O", "O", "O", "O", "O"],
    "park-seulbi":  ["O", "O", "X", "X", "X", "O"],
    "bae-sudam":    ["X", "X", "X", "X", "X", "X"],
    "an-yena":      ["X", "X", "X", "O", "O", "O"],
    "oh-hyunbin":   ["O", "O", "O", "O", "O", "O"],
    "lee-yejun":    ["O", "O", "O", "O", "O", "O"],
    "jung-jaemin":  ["O", "O", "O", "O", "O", "O"],
    "han-gyeol":    ["O", "O", "O", "O", "O", "O"],
    "han-sarang":   ["O", "O", "O", "O", "O", "O"],
}

CSS_TO_ADD = """
    /* === 출석 현황 스타일 === */
    .attendance-section { background: var(--card); border-radius: 14px; padding: 22px 24px; box-shadow: 0 2px 12px rgba(15,31,61,.07); border: 1px solid var(--border); margin-bottom: 20px; page-break-inside: avoid; break-inside: avoid; }
    .attendance-section > label { font-size: 11px; font-weight: 600; letter-spacing: .5px; text-transform: uppercase; color: var(--sub); display: block; margin-bottom: 16px; }
    .attendance-row { display: flex; align-items: flex-start; gap: 12px; flex-wrap: wrap; }
    .attendance-dates { display: flex; gap: 10px; flex-wrap: wrap; flex: 1; }
    .att-date-item { display: flex; flex-direction: column; align-items: center; gap: 6px; }
    .att-date-label { font-size: 11px; font-weight: 600; color: var(--sub); }
    .att-badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; white-space: nowrap; }
    .att-present { background: #ecfdf5; color: #059669; }
    .att-absent  { background: #fef3f2; color: #dc2626; }
    .att-none    { background: #f3f4f6; color: #9ca3af; }
    .attendance-summary { display: flex; flex-direction: column; gap: 6px; padding: 12px 16px; background: #f8faff; border-radius: 10px; border: 1px solid var(--border); font-size: 13px; white-space: nowrap; }
    .att-sum-present { color: #059669; font-weight: 600; }
    .att-sum-absent  { color: #dc2626; font-weight: 600; }
    /* === 피드백 섹션 스타일 === */
    .feedback-section { margin-bottom: 24px; }
    .feedback-section > label { font-size: 11px; font-weight: 600; letter-spacing: .5px; text-transform: uppercase; color: var(--sub); display: block; margin-bottom: 14px; }
    .feedback-card { border-radius: 12px; padding: 18px 20px; margin-bottom: 12px; border: 1px solid var(--border); page-break-inside: avoid; break-inside: avoid; }
    .feedback-card.present { background: var(--card); box-shadow: 0 1px 8px rgba(15,31,61,.06); }
    .feedback-card.absent  { background: #f9fafb; opacity: 0.6; }
    .feedback-card-header  { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
    .feedback-card.absent .feedback-card-header { margin-bottom: 0; }
    .feedback-date { font-size: 14px; font-weight: 700; color: var(--text); }
    .feedback-content { border: 1.5px dashed #d1d5db; border-radius: 8px; padding: 12px; min-height: 60px; color: #9ca3af; font-size: 13px; line-height: 1.6; }
    @media (max-width: 600px) { .attendance-row { flex-direction: column; } .attendance-summary { width: 100%; } }
"""

def status_badge(s):
    if s == "O":
        return '<span class="att-badge att-present">출석</span>'
    elif s == "X":
        return '<span class="att-badge att-absent">결석</span>'
    else:
        return '<span class="att-badge att-none">해당없음</span>'

def make_attendance_section(slug):
    data = ATTENDANCE[slug]
    present_count = data.count("O")
    absent_count  = data.count("X")

    dates_html = ""
    for i, (d, wd) in enumerate(DATES):
        s = data[i]
        dates_html += f"""      <div class="att-date-item">
        <span class="att-date-label">{d}</span>
        {status_badge(s)}
      </div>
"""

    section = f"""  <!-- 출석 현황 섹션 -->
  <div class="attendance-section">
    <label>출석 현황 (수업 6회)</label>
    <div class="attendance-row">
      <div class="attendance-dates">
{dates_html.rstrip()}
      </div>
      <div class="attendance-summary">
        <span class="att-sum-present">출석 {present_count}회</span>
        <span class="att-sum-absent">결석 {absent_count}회</span>
      </div>
    </div>
  </div>
"""
    return section

def make_feedback_section(slug):
    data = ATTENDANCE[slug]

    cards_html = ""
    for i, (d, wd) in enumerate(DATES):
        s = data[i]
        if s == "O":
            badge = '<span class="att-badge att-present">출석</span>'
            card_class = "present"
            content = f"""
      <div class="feedback-content">피드백을 입력하세요.</div>"""
        elif s == "X":
            badge = '<span class="att-badge att-absent">결석</span>'
            card_class = "absent"
            content = ""
        else:
            badge = '<span class="att-badge att-none">해당없음</span>'
            card_class = "absent"
            content = ""

        cards_html += f"""    <div class="feedback-card {card_class}">
      <div class="feedback-card-header">
        <span class="feedback-date">{d} {wd}</span>
        {badge}
      </div>{content}
    </div>
"""

    section = f"""  <!-- 날짜별 피드백 섹션 -->
  <div class="feedback-section">
    <label>날짜별 피드백</label>
{cards_html.rstrip()}
  </div>
"""
    return section

def update_file(slug):
    filepath = f"{BASE_DIR}\\{slug}.html"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # CSS 추가: @media print 바로 앞에 새 CSS 삽입
    # 기존 파일에 이미 추가됐으면 스킵
    if "attendance-section" in content:
        print(f"[SKIP] {slug}.html - 이미 업데이트됨")
        return

    # @media print 블록 찾아서 그 직전에 CSS 삽입
    # 두 가지 패턴 처리: 인라인 스타일 vs 멀티라인 스타일
    content = re.sub(
        r'(\s*)(@media print)',
        CSS_TO_ADD + r'    \2',
        content,
        count=1
    )

    # 새 섹션 HTML 생성
    att_section = make_attendance_section(slug)
    fb_section  = make_feedback_section(slug)
    new_sections = "\n" + att_section + "\n" + fb_section + "\n"

    # back-btn 직전에 삽입
    content = content.replace(
        '  <a class="back-btn" href="../students.html">← 목록으로 돌아가기</a>',
        new_sections + '  <a class="back-btn" href="../students.html">← 목록으로 돌아가기</a>'
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] {slug}.html 업데이트 완료")

if __name__ == "__main__":
    for slug in ATTENDANCE:
        update_file(slug)
    print("\n전체 완료!")
