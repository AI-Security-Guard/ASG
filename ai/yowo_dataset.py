# yowo_dataset.py

import os
import glob
import torch
from torch.utils.data import Dataset
from PIL import Image
import numpy as np
import xml.etree.ElementTree as ET

class YOWODataset(Dataset):
    def __init__(self, root_dir, split='train', sequence_length=16, transform=None, img_size=(224, 224), max_objs=10):
        self.sequence_length = sequence_length
        self.transform = transform
        self.img_size = img_size
        self.max_objs = max_objs
        
        # XML 파일이 있는 labels 폴더를 기준으로 삼습니다.
        self.label_root = os.path.join(root_dir, split, 'labels')
        self.frame_root = os.path.join(root_dir, split, 'frames')
        
        if not os.path.isdir(self.label_root):
            raise ValueError(f"Labels directory not found at: {self.label_root}")

        self.xml_files = sorted(glob.glob(os.path.join(self.label_root, '*.xml')))
        
        # 모든 비디오의 어노테이션 정보를 미리 파싱하여 저장합니다.
        self.annotations = self._parse_all_annotations()
        
        # 학습에 사용할 샘플(비디오 클립) 리스트를 생성합니다.
        self.samples = self._create_samples()

    def _parse_all_annotations(self):
        annotations = {}
        print("Parsing XML annotations...")
        for xml_file in tqdm(self.xml_files, desc="Parsing XMLs"):
            video_name = os.path.splitext(os.path.basename(xml_file))[0]
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            video_annotations = {}
            img_width = int(root.find('size').find('width').text)
            img_height = int(root.find('size').find('height').text)

            # assault를 클래스 인덱스 0으로 가정합니다.
            # 나중에 클래스 추가 시, class_map을 만들어 관리할 수 있습니다.
            class_map = {'assault': 0}

            for track in root.findall('track'):
                label = track.get('label')
                if label not in class_map:
                    continue
                
                class_idx = class_map[label]

                for box in track.findall('box'):
                    frame_idx = int(box.get('frame'))
                    xtl = float(box.get('xtl'))
                    ytl = float(box.get('ytl'))
                    xbr = float(box.get('xbr'))
                    ybr = float(box.get('ybr'))
                    
                    # YOLO 포맷으로 변환: [class, x_center, y_center, width, height]
                    x_center = (xtl + xbr) / 2 / img_width
                    y_center = (ytl + ybr) / 2 / img_height
                    width = (xbr - xtl) / img_width
                    height = (ybr - ytl) / img_height

                    if frame_idx not in video_annotations:
                        video_annotations[frame_idx] = []
                    video_annotations[frame_idx].append([class_idx, x_center, y_center, width, height])
            
            annotations[video_name] = video_annotations
        return annotations

    def _create_samples(self):
        samples = []
        print("Creating training samples...")
        for video_name, video_annotations in tqdm(self.annotations.items(), desc="Creating Samples"):
            video_frame_dir = os.path.join(self.frame_root, video_name)
            frame_paths = sorted(glob.glob(os.path.join(video_frame_dir, '*.jpg')))
            num_frames = len(frame_paths)

            if num_frames < self.sequence_length:
                continue

            for i in range(num_frames - self.sequence_length + 1):
                # 시퀀스 내에 어노테이션이 하나라도 있는지 확인
                has_annotation = False
                for frame_idx_offset in range(self.sequence_length):
                    frame_num = i + frame_idx_offset
                    if frame_num in video_annotations:
                        has_annotation = True
                        break
                
                if has_annotation:
                    samples.append((video_name, i, frame_paths[i:i + self.sequence_length]))
        return samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        video_name, start_frame, frame_paths = self.samples[idx]
        
        images = []
        for frame_path in frame_paths:
            img = Image.open(frame_path).convert('RGB')
            img = img.resize(self.img_size)
            if self.transform:
                img = self.transform(img)
            else:
                img_np = np.array(img)
                img = torch.tensor(img_np).permute(2, 0, 1).float() / 255.0
            images.append(img)
        
        video_tensor = torch.stack(images, dim=0)

        # 라벨 생성: 시퀀스의 마지막 프레임에 해당하는 라벨을 사용
        target = torch.zeros((self.max_objs, 5))
        last_frame_idx = start_frame + self.sequence_length - 1
        
        if video_name in self.annotations and last_frame_idx in self.annotations[video_name]:
            boxes = self.annotations[video_name][last_frame_idx]
            num_boxes = min(len(boxes), self.max_objs)
            for i in range(num_boxes):
                target[i] = torch.tensor(boxes[i])

        return video_tensor, target