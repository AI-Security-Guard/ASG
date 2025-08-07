import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm
import multiprocessing

from core.model import YOWO
from core.region_loss import RegionLoss
from yowo_dataset import YOWODataset
from cfg.defaults import get_cfg

# 함수나 클래스 정의는 바깥에 두어도 괜찮습니다.

def train(cfg, device, batch_size, num_workers):
    # ------------------ 데이터 로딩 ------------------
    print("📦 Loading train dataset...")
    train_dataset = YOWODataset(split="train", root_dir="D:/CCTV/CCTV/yowo_dataset")
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=True if num_workers > 0 else False # num_workers > 0 일 때 True로 설정하면 더 효율적일 수 있습니다.
    )
    print(f"✅ Train samples: {len(train_dataset)}")

    print("📦 Loading val dataset...")
    val_dataset = YOWODataset(split="val", root_dir="D:/CCTV/CCTV/yowo_dataset")
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
    criterion = RegionLoss(cfg).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
    num_epochs = 10

    # ------------------ 학습 루프 ------------------
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        for batch_idx, (videos, labels) in enumerate(tqdm(train_loader, desc=f"[Epoch {epoch+1}/{num_epochs}] Training")):
            videos, labels = videos.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(videos)
            loss = criterion(outputs, labels, epoch, batch_idx, train_loader)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        avg_train_loss = train_loss / len(train_loader)
        print(f"[Epoch {epoch+1}] ✅ Avg Train Loss: {avg_train_loss:.4f}")

        # ------------------ 검증 ------------------
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch_idx, (videos, labels) in enumerate(tqdm(val_loader, desc=f"[Epoch {epoch+1}/{num_epochs}] Validation")):
                videos, labels = videos.to(device), labels.to(device)
                outputs = model(videos)
                loss = criterion(outputs, labels, epoch, batch_idx, val_loader)
                val_loss += loss.item()

        avg_val_loss = val_loss / len(val_loader)
        print(f"[Epoch {epoch+1}] 📉 Avg Val Loss: {avg_val_loss:.4f}")

    # ------------------ 모델 저장 ------------------
    torch.save(model.state_dict(), "yowo_final.pth")
    print("✅ 모델 저장 완료: yowo_final.pth")

# ------------------ 메인 ------------------
if __name__ == "__main__":
    multiprocessing.freeze_support()  # Windows 멀티프로세싱 오류 방지 (가장 먼저 호출하는 것이 좋습니다)

    # ------------------ 설정 ------------------
    cfg = get_cfg()
    cfg.MODEL.NUM_CLASSES = 2
    cfg.MODEL.BACKBONE_2D = "darknet"
    cfg.MODEL.BACKBONE_3D = "resnet18"
    cfg.WEIGHTS.BACKBONE_2D = ""
    cfg.WEIGHTS.BACKBONE_3D = ""
    cfg.WEIGHTS.FREEZE_BACKBONE_2D = False
    cfg.WEIGHTS.FREEZE_BACKBONE_3D = False

    batch_size = 8
    num_workers = 2  # <- 이 값이 0보다 클 때 문제가 발생하므로 구조 변경이 필수

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print(">>> USING RegionLoss from: core.region_loss")
    train(cfg, device, batch_size, num_workers)