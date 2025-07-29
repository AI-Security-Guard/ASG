# 🎥 이상행동 API

업로드된 영상을 분석하여 폭행 구간을 자동 감지하는 AI  모델입니다. Flask 기반 API로 구성되어 있으며, 학습된 PyTorch 모델을 사용합니다.

---

## 📁 폴더 구조

```
ai/
├── app.py               # Flask 서버 진입점
├── api/
│   ├── upload.py        # 영상 업로드 저장
│   └── analyze.py       # 모델 실행 및 폭행구간 탐지
├── model/
│   └── model.pth        # 학습된 PyTorch 모델 가중치
├── models/              # 논문 참고한 DFWSGAR모델 정의
├── utils/
│   ├── model_utils.py   # 모델 로딩 및 설정 함수
│   └── video_utils.py   # 프레임 추출 및 클립 저장
├── uploads/             # 클라이언트가 업로드한 영상 저장 경로
└── clips/               # 분석된 폭행 구간 영상 클립 저장 경로
```

---

## 🚀 실행 방법

1. Python 환경 구성
```bash
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
```

2. 서버 실행
```bash
python app.py
```

---

## 🧪 API 사용법

### 1. `/upload` - 영상 업로드
- `POST /upload`
- form-data: `video=<파일>`

### 2. `/analyze` - 분석 실행
- `POST /analyze`
- form-data: `video=<파일>`

#### 응답 예시:
```json
{
  "assault_intervals": [
    {
      "start_frame": 90,
      "end_frame": 150,
      "start_time": "00:03",
      "end_time": "00:05"
    }
  ]
}
```



---

## 🛠 기타 참고 사항

- 영상 분석은 평균 8~20분 내외 소요됩니다. (4K 5분 영상 기준)
- 컴퓨터 사양에 따라서 더 짧거나 길어질 수 있습니다.

---

## 📄 requirements.txt
```
flask
torch
torchvision
opencv-python
numpy
scikit-learn
```



