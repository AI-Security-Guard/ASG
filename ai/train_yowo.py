# train_yowo.py (Path updated)

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm
import multiprocessing
import numpy as np

# 원래의 RegionLoss를 다시 사용
from core.region_loss import RegionLoss 
from core.model import YOWO
from yowo_dataset import YOWODataset
from cfg.defaults import get_cfg

def train(cfg, device, batch_size, num_workers):
    # ------------------ 데이터 로딩 ------------------
    print("📦 Loading train dataset...")
    # [수정] 데이터셋 경로를 새로운 경로로 변경합니다.
    train_dataset = YOWODataset(split="train", root_dir="D:/CCTV/CCTV/sample_dataset")
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=True if num_workers > 0 else False
    )
    print(f"✅ Train samples: {len(train_dataset)}")

    print("📦 Loading val dataset...")
    # [수정] 검증 데이터셋 경로도 새로운 경로로 변경합니다.
    val_dataset = YOWODataset(split="val", root_dir="D:/CCTV/CCTV/sample_dataset")
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=True if num_workers > 0 else False
    )
    print(f"✅ Val samples: {len(val_dataset)}")

    # ------------------ 모델 및 손실 함수 ------------------
    model = YOWO(cfg).to(device)
    # 손실 함수를 RegionLoss로 복원
    criterion = RegionLoss(cfg).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
    num_epochs = 10

    # ------------------ 학습 루프 ------------------
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        # tqdm을 위해 np.mean 사용 준비
        loss_meter = []
        for batch_idx, (videos, labels) in enumerate(tqdm(train_loader, desc=f"[Epoch {epoch+1}/{num_epochs}] Training")):
            videos = videos.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(videos)
            
            # 손실 함수 호출을 원래의 탐지 방식에 맞게 복원
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            loss_meter.append(loss.item())
            # tqdm에 평균 손실 표시
            tqdm_description = f"[Epoch {epoch+1}/{num_epochs}] Training - Loss: {np.mean(loss_meter):.4f}"
            train_loader.set_description(tqdm_description)


        avg_train_loss = train_loss / len(train_loader)
        print(f"\n[Epoch {epoch+1}] ✅ Avg Train Loss: {avg_train_loss:.4f}")

        # ------------------ 검증 ------------------
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch_idx, (videos, labels) in enumerate(tqdm(val_loader, desc=f"[Epoch {epoch+1}/{num_epochs}] Validation")):
                videos = videos.to(device)
                labels = labels.to(device)
                
                outputs = model(videos)
                loss = criterion(outputs, labels)
                val_loss += loss.item()

        avg_val_loss = val_loss / len(val_loader)
        print(f"[Epoch {epoch+1}] 📉 Avg Val Loss: {avg_val_loss:.4f}")

    # ------------------ 모델 저장 ------------------
    torch.save(model.state_dict(), "yowo_detector_final.pth")
    print("✅ 모델 저장 완료: yowo_detector_final.pth")

# ------------------ 메인 ------------------
if __name__ == "__main__":
    multiprocessing.freeze_support()

    # ------------------ 설정 ------------------
    cfg = get_cfg()
    # assault 클래스 하나만 있으므로 1로 설정
    cfg.MODEL.NUM_CLASSES = 1
    cfg.MODEL.BACKBONE_2D = "darknet"
    cfg.MODEL.BACKBONE_3D = "resnet18"
    
    batch_size = 8
    # XML 파싱, 프레임 로딩 등 복잡한 작업을 하므로, 안정성을 위해 num_workers=0으로 시작하는 것을 권장합니다.
    # 학습이 안정적으로 시작되면 이 값을 2, 4 등으로 늘려 속도를 높일 수 있습니다.
    num_workers = 0 

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f">>> USING Device: {device}")
    
    train(cfg, device, batch_size, num_workers)