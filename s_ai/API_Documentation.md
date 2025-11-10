# 🧠 AI Security Guard – Flask API 문서

본 문서는 **AI 기반 영상 내 거동 수상자 감지 시스템**의 Flask 서버(`analyze.py`, `routes.py`, `app.py`)에 대한 전체 API 명세서입니다.

---

## 📁 프로젝트 폴더 구조

```
ASG/
├── app.py                # Flask 앱 초기화 (CORS, DB 설정, Blueprint 등록)
├── analyze.py            # DFWSGAR 모델 로드 및 영상 분석 로직
├── routes.py             # Flask API 라우팅 정의
├── database.py           # SQLAlchemy DB 인스턴스 초기화
├── jobs.db               # SQLite3 데이터베이스 파일
├── models/
│   ├── models.py         # DFWSGAR 모델 구조 정의
│   ├── analysis.py       # SQLAlchemy ORM 모델 (Job, Clip)
├── utils/
│   └── utils.py          # 영상 분석에 필요한 유틸 함수
├── analyzed_videos/      # 분석된 주석 영상 저장 폴더
├── event_clips/          # 비정상(assault) 구간 클립 저장 폴더
├── thumbnails/           # 각 클립 썸네일 저장 폴더
└── model/
    ├── best_model.pth    # 학습된 DFWSGAR 모델 가중치
    └── best_threshold.txt # assault 판별 임계값
```

---

## 🧩 데이터베이스 모델 구조

### `Job` 테이블
| 필드명 | 타입 | 설명 |
|--------|------|------|
| job_id | VARCHAR (PK) | 각 분석 작업의 고유 ID |
| username | TEXT | 분석 요청을 보낸 사용자명 |
| video_path | TEXT | 원본 영상 파일 경로 |
| annotated_video | TEXT | 분석 후 생성된 주석 영상 파일 경로 |
| progress | FLOAT | 분석 진행률 (0 ~ 100) |
| status | TEXT | 상태값: `running`, `done`, `error` |
| results | JSON | 분석 결과 (clips 메타데이터 등) |
| message | TEXT | 오류 메시지 또는 기타 상태 메시지 |

### `Clip` 테이블
| 필드명 | 타입 | 설명 |
|--------|------|------|
| id | INTEGER (PK) | 클립 고유 ID |
| job_id | VARCHAR | Job과의 관계 (외래키) |
| class_name | TEXT | 탐지된 행동 클래스명 (예: assault) |
| start_time | TEXT | 클립 시작 시점 (HH:MM:SS) |
| start_x / start_y | INTEGER | 감지된 객체의 시작 좌표 |
| start_w / start_h | INTEGER | 감지된 영역의 너비/높이 |
| clip_name | TEXT | 클립 파일 이름 |
| clip_path | TEXT | 클립 절대 경로 |
| thumbnail | TEXT | 썸네일 파일 경로 |
| checked | BOOLEAN | 검수 여부 (PATCH로 변경 가능) |

---

## ⚙️ API 목록

### 1️⃣ **POST /analyze**
영상 분석 요청 (백그라운드 스레드에서 실행)

#### 요청 바디
```json
{
  "video_path": "C:/Users/sojeong/Documents/video.mp4",
  "username": "sojeong"
}
```

#### 성공 응답 (202 Accepted)
```json
{
  "job_id": "d8f41d29-1d30-44d2-8bfb-123456789abc",
  "status": "running",
  "progress": 0,
  "results": null
}
```

#### 실패 응답 예시
| 상태 코드 | 상황 | 응답 예시 |
|------------|------|------------|
| 404 | 파일 없음 | `{"detail": "Video file not found: ..."}` |
| 503 | 모델 미로드 | `{"detail": "Model not loaded"}` |
| 500 | 내부 오류 | `{"detail": "Internal Server Error"}` |

---

### 2️⃣ **GET /jobs/<job_id>**
특정 작업의 진행 상황 및 결과 조회

#### 응답 예시
```json
{
  "job_id": "d8f41d29-1d30-44d2-8bfb-123456789abc",
  "video_path": "C:/Users/sojeong/Documents/video.mp4",
  "status": "done",
  "progress": 100.0,
  "annotated_video_url": "/analyzed_videos/test_analyze.mp4",
  "result": [
    {
      "clip_id": 1,
      "class_name": "assault",
      "start_time": "00:00:08",
      "bbox": [120, 200, 300, 480],
      "clip_url": "/event_clips/test_clip1.mp4",
      "thumb_url": "/event_thumbs/test_clip1_thumb.jpg",
      "checked": false
    }
  ]
}
```

---

### 3️⃣ **GET /jobs/<job_id>/clips**
특정 작업의 클립 리스트만 조회

#### 응답 예시
```json
{
  "job_id": "d8f41d29-1d30-44d2-8bfb-123456789abc",
  "video_path": "C:/Users/.../video.mp4",
  "count": 2,
  "clips": [
    {
      "id": 1,
      "class_name": "assault",
      "clip_url": "/event_clips/test_clip1.mp4",
      "thumb_url": "/event_thumbs/test_clip1_thumb.jpg",
      "checked": true
    }
  ]
}
```

---

### 4️⃣ **PATCH /clips/<clip_id>/check**
특정 클립을 검수 완료 상태로 표시

#### 응답 예시
```json
{
  "message": "checked set to true",
  "clip_id": 1,
  "checked": true
}
```

---

### 5️⃣ **GET /jobs/latest?username=<username>**
해당 사용자의 가장 최근 Job ID를 조회

#### 응답 예시
```json
{"job_id": "a9b71d92-124d-4f2c-bd4c-8f8a7cb17c56"}
```

---

### 6️⃣ **GET /event_clips/<filename>**
생성된 클립 영상 스트리밍 (Range 지원)

### 7️⃣ **GET /event_thumbs/<filename>**
썸네일 이미지 파일 제공

### 8️⃣ **GET /analyzed_videos/<filename>**
분석 완료된 전체 영상(주석 포함) 스트리밍

---

## 🔒 에러 및 상태 코드 요약

| 코드 | 의미 | 설명 |
|------|------|------|
| 200 | OK | 정상 처리 |
| 202 | Accepted | 백그라운드 분석 시작 |
| 400 | Bad Request | 필수 인자 누락 |
| 404 | Not Found | Job/Clip/파일 없음 |
| 500 | Internal Server Error | 서버 내부 오류 |
| 503 | Service Unavailable | 모델 미로드 |

---

© 2025 AI-Security-Guard Project Team
