# yowo_dataset.py 파일

import os
import glob
import torch
from torch.utils.data import Dataset
from PIL import Image
import numpy as np # NumPy를 임포트해야 합니다.

class YOWODataset(Dataset):
    def __init__(self, root_dir, split='train', sequence_length=16, transform=None, max_objs=1, img_size=(224, 224)):
        self.sequence_length = sequence_length
        self.transform = transform
        self.max_objs = max_objs
        self.img_size = img_size # 이미지 크기를 저장할 변수 추가
        self.samples = []

        frame_root = os.path.join(root_dir, split, 'frames')
        label_root = os.path.join(root_dir, split, 'labels')

        video_folders = sorted(os.listdir(frame_root))

        for video_name in video_folders:
            frame_dir = os.path.join(frame_root, video_name)
            label_dir = os.path.join(label_root, video_name)

            frame_paths = sorted(glob.glob(os.path.join(frame_dir, '*.jpg')))
            
            # 레이블 파일 경로는 프레임 경로로부터 생성 (레이블이 없는 경우 대비)
            # label_paths = sorted(glob.glob(os.path.join(label_dir, '*.txt')))

            if len(frame_paths) < sequence_length:
                continue

            for i in range(len(frame_paths) - sequence_length + 1):
                frame_seq = frame_paths[i:i + sequence_length]
                
                # 시퀀스 내 하나라도 1이면 행동이 있다고 간주
                is_abnormal = False
                for frame_path in frame_seq:
                    # 레이블 파일 경로를 프레임 파일 경로 기반으로 구성
                    label_path = frame_path.replace('frames', 'labels').replace('.jpg', '.txt')
                    if os.path.exists(label_path):
                        with open(label_path, 'r') as f:
                            if f.read().strip() == '1':
                                is_abnormal = True
                                break
                
                self.samples.append((frame_seq, is_abnormal))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        # 💡 [수정] 전체 __getitem__ 함수를 이 코드로 교체하세요.
        try:
            frame_seq_paths, is_abnormal = self.samples[idx]
            images = []

            for frame_path in frame_seq_paths:
                img = Image.open(frame_path).convert('RGB')
                
                # 이미지를 리사이즈합니다 (모든 이미지 크기 통일)
                img = img.resize(self.img_size)

                if self.transform:
                    img = self.transform(img)
                else:
                    # 💡 [수정 1] PIL 이미지를 NumPy 배열로 변환 후 텐서로 만듭니다.
                    img_np = np.array(img)
                    img = torch.tensor(img_np).permute(2, 0, 1).float() / 255.0
                
                images.append(img)

            # [T, C, H, W]
            video_tensor = torch.stack(images, dim=0)

            # ---------- 라벨 생성 (YOLO 포맷용) ----------
            # [class, x_center, y_center, w, h]
            target = torch.zeros((self.max_objs, 5))
            if is_abnormal:
                # 전체 프레임을 bbox로 가정
                target[0] = torch.tensor([1, 0.5, 0.5, 1.0, 1.0])

            return video_tensor, target

        except Exception as e:
            # 💡 [수정 2] 'index'를 'idx'로 변경했습니다.
            print(f"🚨 [Dataset Error] Corrupted data at index {idx}. Error: {e}. Skipping.")
            
            # 💡 [수정 3] 오류 발생 시에도 정상 데이터와 동일한 모양의 '더미' 텐서를 반환합니다.
            dummy_video = torch.zeros((self.sequence_length, 3, self.img_size[1], self.img_size[0]))
            dummy_target = torch.zeros((self.max_objs, 5))
            return dummy_video, dummy_target