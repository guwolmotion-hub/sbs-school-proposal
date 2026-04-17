# SBS아카데미컴퓨터아트학원 구월지점 — 수강생 관리 시스템 명세서

> **주의**: 이 파일은 현재 시스템의 완성 상태를 기록한 명세서입니다.
> 기능 추가·디자인 수정 시 **아래 명시된 데이터(시드 데이터, 수강생 정보, 피드백 내용)는 절대 건드리지 않습니다.**

---

## 배포 정보

| 항목 | 값 |
|------|-----|
| GitHub 저장소 | `guwolmotion-hub/sbs-school-proposal` |
| 배포 URL | `https://guwolmotion-hub.github.io/sbs-school-proposal/` |
| 브랜치 | `main` |
| 배포 방식 | GitHub Pages (push 즉시 반영) |

---

## 파일 구조

```
sbs-school-proposal/
├── main.html           # 홈 대시보드 (수강생 수 · 포트폴리오 수 통계)
├── students.html       # 수강생 관리 메인 페이지
├── portfolio.html      # 포트폴리오 갤러리 페이지
├── firebase-config.js  # Firebase 설정 (공통 사용)
├── index.html          # (구) 슬라이드 제안서
├── school-intro.html   # 학원 소개 페이지
└── PROJECT_SPEC.md     # 이 파일
```

---

## Firebase 설정

- **프로젝트 ID**: `portfolioguwol`
- **Firestore 컬렉션**:
  - `sbs_students` — 수강생 데이터
  - `sbs_portfolio` — 포트폴리오 아이템
- **보안 규칙**: `allow read, write: if true` (인증 없이 읽기/쓰기 허용)
- **Firebase Storage**: 미사용 (유료 플랜 필요) → Cloudinary 대체

### Cloudinary 설정 (이미지/영상 업로드)
- **Cloud name**: `ditmabkad`
- **Upload preset**: `Portfolio` (unsigned)
- **업로드 엔드포인트**: `https://api.cloudinary.com/v1_1/ditmabkad/auto/upload`

---

## 학과 목록 (DEPTS) — 순서 및 색상 고정

| 학과명 | 사이드바 색상 |
|--------|-------------|
| 영상/모션2D | `#3a7bd5` (파랑) |
| 영상/모션3D | `#7c3aed` (보라) |
| 시각편집 | `#e8562a` (주황) |
| 아트웍 | `#059669` (초록) |
| 인테리어 | `#d97706` (노랑) |
| CG/마야 | `#dc2626` (빨강) |
| 웹 | `#0891b2` (청록) |

> 학과 목록 · 순서 · 색상은 수정하지 않습니다.

---

## 수강생 관리 (students.html)

### 레이아웃 구조
```
┌─────────────┬────────────────────────────────────┐
│  사이드바    │  상단바 (수강생 관리 / 날짜 / 학생추가)│
│  (256px)    ├────────────────────────────────────┤
│             │  Hero 배너                          │
│  학과 목록  │                                    │
│   └ 년도    │  #app (동적 렌더링 영역)             │
│      └ 월   │                                    │
│         명수│                                    │
│             │                                    │
│  [홈]       │                                    │
│  [포트폴리오]│                                    │
└─────────────┴────────────────────────────────────┘
```

### 사이드바 네비게이션 계층 구조
```
학과 (클릭 → 펼침/접힘)
  └ 년도 (클릭 → 펼침/접힘)
       └ 월  n명  (클릭 → 콘텐츠 영역 갱신)
       └ ...
       └ + 년도 추가
```
- 학과·년도·월 모두 사이드바에서만 선택 (콘텐츠 영역에 탭/버튼 없음)
- 월 옆에 해당 월 수강생 수(명) 실시간 표시
- "+ 년도 추가": prompt()로 년도 입력 → `YEARS` 배열에 추가 (런타임 유지)

### 상태 변수
```javascript
let TAB   = DEPTS[0];   // 현재 선택된 학과 (기본: 영상/모션2D)
let YEAR  = null;       // 선택된 년도 (null이면 "년도를 선택하세요" 표시)
let MONTH = null;       // 선택된 월 (null이면 "월을 선택하세요" 표시)
let SUBTAB = 'admission'; // 'admission' | 'employ' | 'transfer'
let YEARS = [2026];     // 사용 가능한 년도 목록 (추가 가능)
```

### 콘텐츠 영역 렌더링 흐름
1. **YEAR === null** → "년도를 선택하세요" 안내
2. **YEAR 선택, MONTH === null** → "월을 선택하세요" 안내
3. **YEAR + MONTH 선택** → 입시반/취업반/편입반 탭 + 수강생 테이블

### 수강생 타입
| 코드 | 표시 | 설명 |
|------|------|------|
| `admission` | 입시반 | type==='admission' |
| `employ` + goal!=='편입' | 취업반 | type==='employ' |
| `employ` + goal==='편입' | 편입반 | type==='employ' |

### 수강생 데이터 구조
```javascript
{
  id: string,          // 고유 ID (s + timestamp36 + random)
  name: string,        // 이름
  dept: string,        // 학과 (DEPTS 중 하나)
  year: number,        // 년도 (예: 2026)
  month: number,       // 월 (예: 3)
  type: 'admission' | 'employ',
  mentor: string,      // 담당 멘토
  age: number,
  contact: string,     // 연락처
  topic: string,       // 포트폴리오 주제
  stage: 'plan' | 'making' | 'revise' | 'done',
  pct: number,         // 진행률 0~100
  goal: string | null, // 취업/편입 목표
  days: [              // 수업일 목록
    { date: 'MM-DD', day: '월|화|...', holiday: boolean }
  ],
  attendance: { 'MM-DD': 'present' | 'absent' | 'holiday' | 'pending' },
  feedback: { 'MM-DD': { text: string, media: [] } }
}
```

### 수업일 추가 (openAddClassDay)
- **날짜 입력**: 1일차~8일차 날짜를 사용자가 직접 입력 (MM-DD 형식)
- **요일 자동 계산**: 입력한 날짜 기준으로 요일 자동 계산
- auto-fill 없음 — 사용자가 직접 타이핑

### DB 객체 (Firebase Firestore 연동)
```javascript
const DB = {
  _cache: null,          // 인메모리 캐시 (deep copy 반환)
  get() { ... },         // JSON.parse(JSON.stringify(cache)) 반환
  save(data) { ... },    // Firestore sbs_students에 저장
  load() { ... },        // Firestore에서 불러와 캐시 초기화
  reset() { ... }        // SEED 데이터로 초기화
}
```
- `get()`은 항상 deep copy 반환 (참조 공유 버그 방지)

---

## 포트폴리오 (portfolio.html)

### 레이아웃
- 동일한 사이드바 구조 (학과 탭)
- 이미지/영상 업로드: Cloudinary 사용
- Firestore 컬렉션: `sbs_portfolio`

### 포트폴리오 아이템 구조
```javascript
{
  id: string,
  dept: string,
  title: string,
  desc: string,
  mediaUrl: string,   // Cloudinary URL
  mediaType: 'image' | 'video',
  createdAt: timestamp
}
```

---

## 홈 (main.html)

- 총 수강생 수: `sbs_students` 컬렉션 size
- 포트폴리오 작업물 수: `sbs_portfolio` 컬렉션 size
- 학과 수: 7 (고정)
- 사이드바 학과 클릭 → `localStorage.setItem('sbs_nav_dept', dept)` → `students.html`로 이동

---

## 시드 데이터 (SEED) — 절대 수정 금지

`students.html` 내 `const SEED = { students: [...] }` 블록에 실제 수강생 13명의 데이터가 포함되어 있습니다.

**포함된 수강생 (ID 기준)**:
`kim-siwoo`, `nam-jaeseo`, `an-yena`, `lee-yejun`, `kim-geonwoo`, `kim-sumin`, `han-sarang`, `bae-sudam`, `han-gyeol`, `noh-wontae`, `park-seulbi`, `jung-jaemin`, `oh-hyunbin`

> ⚠️ SEED 데이터 블록(이름, 연락처, 피드백 텍스트, 출결 기록 등)은 **어떠한 작업에서도 수정하지 않습니다.**
> 기능 추가/수정 시에는 SEED 블록 위아래의 로직만 건드립니다.

---

## BASE_DAYS (기본 수업일) — 절대 수정 금지

```javascript
const BASE_DAYS = [
  {date:'03-17', day:'월', holiday:false},
  {date:'03-19', day:'수', holiday:false},
  {date:'03-24', day:'월', holiday:false},
  {date:'03-26', day:'수', holiday:false},
  {date:'03-31', day:'월', holiday:true},   // 휴강
  {date:'04-02', day:'수', holiday:false},
  {date:'04-07', day:'월', holiday:false},
  {date:'04-09', day:'수', holiday:false},
];
```

---

## 주요 함수 목록

| 함수 | 파일 | 역할 |
|------|------|------|
| `initSidebar()` | students.html | 사이드바 학과→년도→월 트리 렌더링 |
| `addYear()` | students.html | 새 년도 추가 (prompt) |
| `setTab(dept)` | students.html | 학과 전환 (YEAR·MONTH 초기화) |
| `setYear(y)` | students.html | 년도 선택 (MONTH 초기화) |
| `setMonth(m)` | students.html | 월 선택 → 테이블 표시 |
| `setSubTab(t)` | students.html | 입시/취업/편입반 전환 |
| `renderList()` | students.html | 목록 뷰 렌더링 |
| `renderStudentDetail(id)` | students.html | 학생 상세 뷰 렌더링 |
| `openAddStudent()` | students.html | 학생 추가 모달 |
| `openAddClassDay(id)` | students.html | 수업일 추가 모달 |
| `_commitMedia(files)` | students.html | Cloudinary 파일 업로드 |

---

## 작업 규칙 (앞으로의 수정 원칙)

1. **SEED 데이터 블록 수정 금지** — 실제 수강생 이름·연락처·피드백 내용 포함
2. **BASE_DAYS 수정 금지** — 실제 수업일 기록
3. **DEPTS 배열 순서·색상 수정 금지** — 학과 목록 고정
4. **Firebase 설정 수정 금지** — `firebase-config.js` 그대로 유지
5. 기능 추가 시: 기존 함수 로직을 파악한 뒤 최소 범위만 수정
6. 배포: 수정 후 반드시 `git add → commit → push` 완료
7. 큰 변경은 Write 전체 재작성, 소규모 수정은 Edit 사용
