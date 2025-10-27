# 🧠 AI Security Guard (ASG) — Video Analysis API

AI Security Guard는 영상 내에서 **폭행(assault)** 등 이상 행동을 자동 감지하고,  
감지 구간을 클립으로 저장해 결과를 반환하는 Flask 기반 AI 분석 서버입니다.

---

## 📁 API Base URL

```
http://127.0.0.1:5001
```

---

## 🔍 1. 분석 요청

**POST /analyze**

원본 영상을 업로드하거나 기존 영상 경로를 전달하여 분석 작업을 시작합니다.

### 요청 예시

```json
{
    "video_path": "10-1_Cam03_Assault03_Place07_Night_Summer.mp4"
}
```

### 응답 예시

```json
{
    "job_id": "868447d3-0e23-4307-9e90-e27634199275",
    "status": "running",
    "progress": 0.0,
    "video_path": "10-1_Cam03_Assault03_Place07_Night_Summer.mp4"
}
```

### 설명

| 필드명       | 타입   | 설명                                   |
| ------------ | ------ | -------------------------------------- |
| `job_id`     | string | 분석 작업의 고유 ID                    |
| `status`     | string | 현재 상태 (`running`, `done`, `error`) |
| `progress`   | float  | 분석 진행률 (0.0~100.0)                |
| `video_path` | string | 분석 대상 원본 영상 경로               |

---

## 🔄 2. 작업 상태 조회

**GET /jobs/<job_id>**

특정 영상 분석 작업의 상태와 결과를 조회합니다.

---

### ▶ 진행 중 예시

```json
{
    "job_id": "e7034efc-1b24-4288-b7f2-37118b8123f6",
    "status": "running",
    "progress": 40.03,
    "annotated_video": null,
    "video_path": "10-1_Cam03_Assault03_Place07_Night_Summer.mp4",
    "result": []
}
```

---

### ✅ 완료 예시

```json
{
    "job_id": "868447d3-0e23-4307-9e90-e27634199275",
    "status": "done",
    "progress": 100.0,
    "annotated_video": "analyzed_videos/10-1_Cam03_Assault03_Place07_Night_Summer_analyze.mp4",
    "video_path": "10-1_Cam03_Assault03_Place07_Night_Summer.mp4",
    "result": [
        {
            "clip_id": 7,
            "class_name": "assault",
            "start_time": "00:00:12",
            "bbox": [312, 118, 470, 236],
            "clip_url": "event_clips/10-1_Cam03_Assault03_Place07_Night_Summer_clip1.mp4",
            "thumbnail": "thumbnails/10-1_Cam03_Assault03_Place07_Night_Summer_clip1_thumb.jpg"
        }
    ]
}
```

---

### 필드 설명

#### 🔹 상위 필드

| 필드명            | 타입   | 설명                                 |
| ----------------- | ------ | ------------------------------------ |
| `job_id`          | string | 작업 고유 ID                         |
| `status`          | string | 상태 (`running`, `done`, `error`)    |
| `progress`        | float  | 분석 진행률                          |
| `annotated_video` | string | 분석 결과 영상 (감지 구간 표시 포함) |
| `video_path`      | string | 원본 영상 경로                       |
| `result`          | array  | 탐지된 클립 목록                     |

#### 🔸 result 배열 필드

| 필드명       | 타입    | 설명                                   |
| ------------ | ------- | -------------------------------------- |
| `clip_id`    | integer | 클립 ID                                |
| `class_name` | string  | 감지된 행동 클래스명 (예: `"assault"`) |
| `start_time` | string  | 감지 시작 시각 (`HH:MM:SS`)            |
| `bbox`       | array   | 바운딩 박스 좌표 [x1, y1, x2, y2]      |
| `clip_url`   | string  | 감지 구간 클립 영상 경로               |
| `thumbnail`  | string  | 클립 썸네일 이미지 경로                |

---

## 🧩 status 종류

| 상태      | 설명           |
| --------- | -------------- |
| `running` | 분석이 진행 중 |
| `done`    | 분석 완료      |
| `error`   | 오류 발생      |

---

## 🗂️ 저장 구조 (기본 경로)

| 항목     | 기본 디렉터리      | 예시                                                        |
| -------- | ------------------ | ----------------------------------------------------------- |
| 분석영상 | `/analyzed_videos` | `10-1_Cam03_Assault03_Place07_Night_Summer_analyze.mp4`     |
| 클립     | `/event_clips`     | `10-1_Cam03_Assault03_Place07_Night_Summer_clip1.mp4`       |
| 썸네일   | `/thumbnails`      | `10-1_Cam03_Assault03_Place07_Night_Summer_clip1_thumb.jpg` |

---

## 🎬 3. 클립 목록만 조회

**GET /jobs/<job_id>/clips**

특정 작업에 대해 클립 목록만 별도로 조회합니다.
clip_url, thumb_url은 각각 클립 스트리밍/썸네일 라우트로 연결됩니다.

---

### ▶ 응답 예시

```json
{
    "job_id": "868447d3-0e23-4307-9e90-e27634199275",
    "video_path": "10-1_Cam03_Assault03_Place07_Night_Summer.mp4",
    "count": 1,
    "clips": [
        {
            "id": 7,
            "job_id": "868447d3-0e23-4307-9e90-e27634199275",
            "class_name": "assault",
            "start_time": "00:00:12",
            "start_x": 312,
            "start_y": 118,
            "start_w": 158,
            "start_h": 118,
            "clip_name": "10-1_Cam03_Assault03_Place07_Night_Summer_clip1.mp4",
            "thumbnail": "10-1_Cam03_Assault03_Place07_Night_Summer_clip1_thumb.jpg",
            "clip_url": "/event_clips/10-1_Cam03_Assault03_Place07_Night_Summer_clip1.mp4",
            "thumb_url": "/event_thumbs/10-1_Cam03_Assault03_Place07_Night_Summer_clip1_thumb.jpg"
        }
    ]
}
```

---

## 📷 4. 썸네일 조회

**GET /event_thumbs/<fname>**

클립 썸네일 이미지를 반환합니다.

---

### ▶ 응답 예시

```json
{}
```

---

### 🎬 5. 클립 목록 조회

**GET /jobs/<job_id>/clips**

특정 분석 작업의 클립 목록만 별도로 조회합니다.
clip_url, thumb_url은 각각 클립 스트리밍과 썸네일 이미지에 접근할 수 있는 엔드포인트입니다.

```json
{
    "job_id": "868447d3-0e23-4307-9e90-e27634199275",
    "video_path": "10-1_Cam03_Assault03_Place07_Night_Summer.mp4",
    "count": 1,
    "clips": [
        {
            "id": 7,
            "job_id": "868447d3-0e23-4307-9e90-e27634199275",
            "class_name": "assault",
            "start_time": "00:00:12",
            "start_x": 312,
            "start_y": 118,
            "start_w": 158,
            "start_h": 118,
            "clip_name": "10-1_Cam03_Assault03_Place07_Night_Summer_clip1.mp4",
            "thumbnail": "10-1_Cam03_Assault03_Place07_Night_Summer_clip1_thumb.jpg",
            "clip_url": "/event_clips/10-1_Cam03_Assault03_Place07_Night_Summer_clip1.mp4",
            "thumb_url": "/event_thumbs/10-1_Cam03_Assault03_Place07_Night_Summer_clip1_thumb.jpg"
        }
    ]
}
```

---
