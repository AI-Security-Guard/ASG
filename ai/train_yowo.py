# train_yowo.py (Final fix for tqdm)

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm
import multiprocessing
import numpy as np

from core.model import YOWO
from yowo_dataset import YOWODataset
from cfg.defaults import get_cfg

def train(cfg, device, batch_size, num_workers):
    # ------------------ 데이터 로딩 ------------------
    print("📦 Loading train dataset...")
    train_dataset = YOWODataset(split="train", root_dir="D:/CCTV/CCTV/sample_dataset")
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=True if num_workers > 0 else False,
    )
    print(f"✅ Train samples: {len(train_dataset)}")

    print("📦 Loading val dataset...")
    val_dataset = YOWODataset(split="val", root_dir="D:/CCTV/CCTV/sample_dataset")
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=True if num_workers > 0 else False,
    )
    print(f"✅ Val samples: {len(val_dataset)}")

    # ------------------ 모델 및 손실 함수 ------------------
    model = YOWO(cfg).to(device)
    criterion = nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
    num_epochs = 10

    # ------------------ 학습 루프 ------------------
    for epoch in range(num_epochs):
        model.train()
        loss_meter = []
        
        # [수정] tqdm 객체를 progress_bar 변수에 저장합니다.
        progress_bar = tqdm(train_loader, desc=f"[Epoch {epoch+1}/{num_epochs}] Training")
        
        for batch_idx, (videos, labels) in enumerate(progress_bar):
            videos = videos.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(videos)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            loss_meter.append(loss.item())
            
            # [수정] train_loader가 아닌 progress_bar 변수에 설명을 설정합니다.
            tqdm_description = f"[Epoch {epoch+1}/{num_epochs}] Training - Loss: {np.mean(loss_meter):.4f}"
            progress_bar.set_description(tqdm_description)

        print(f"\n[Epoch {epoch+1}] ✅ Avg Train Loss: {np.mean(loss_meter):.4f}")

        # ------------------ 검증 ------------------
        model.eval()
        val_loss_meter = []
        correct_predictions = 0
        total_predictions = 0
        with torch.no_grad():
            for batch_idx, (videos, labels) in enumerate(tqdm(val_loader, desc=f"[Epoch {epoch+1}/{num_epochs}] Validation")):
                videos = videos.to(device)
                labels = labels.to(device)
                
                outputs = model(videos)
                loss = criterion(outputs, labels)
                val_loss_meter.append(loss.item())

                _, predicted = torch.max(outputs.data, 1)
                total_predictions += labels.size(0)
                correct_predictions += (predicted == labels).sum().item()

        accuracy = 100 * correct_predictions / total_predictions if total_predictions > 0 else 0
        print(f"[Epoch {epoch+1}] 📉 Avg Val Loss: {np.mean(val_loss_meter):.4f} | 🎯 Accuracy: {accuracy:.2f}%")

    torch.save(model.state_dict(), "action_classifier_final.pth")
    print("✅ 모델 저장 완료: action_classifier_final.pth")

if __name__ == "__main__":
    multiprocessing.freeze_support()

    cfg = get_cfg()
    cfg.MODEL.NUM_CLASSES = 6
    cfg.MODEL.BACKBONE_3D = "resnet18"
    
    batch_size = 8
    num_workers = 8

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f">>> USING Device: {device}")
    
    train(cfg, device, batch_size, num_workers)