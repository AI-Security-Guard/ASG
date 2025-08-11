# yowo_dataset.py (Final Classification Version)

import os
import glob
import torch
from torch.utils.data import Dataset
from PIL import Image
import numpy as np
import xml.etree.ElementTree as ET
from tqdm import tqdm

class YOWODataset(Dataset):
    def __init__(self, root_dir, split='train', sequence_length=16, transform=None, img_size=(224, 224)):
        self.sequence_length = sequence_length
        self.transform = transform
        self.img_size = img_size
        
        self.label_root = os.path.join(root_dir, split, 'labels')
        self.frame_root = os.path.join(root_dir, split, 'frames')
        
        if not os.path.isdir(self.label_root):
            raise ValueError(f"Labels directory not found at: {self.label_root}")

        self.xml_files = sorted(glob.glob(os.path.join(self.label_root, '*.xml')))
        
        # 클래스 이름을 정수 인덱스로 매핑합니다.
        self.class_map = {
            'punching': 0, 'kicking': 1, 'pulling': 2, 'pushing': 3, 
            'throwing': 4, 'falldown': 5
            # 필요에 따라 다른 클래스 추가
        }
        
        self.annotations = self._parse_all_annotations()
        self.samples = self._create_samples()
        
        if not self.samples:
            raise RuntimeError("Failed to create any samples. Please check XML annotations and file paths.")

    def _parse_all_annotations(self):
        annotations = {}
        print("Parsing XML annotations...")
        for xml_file in tqdm(self.xml_files, desc="Parsing XMLs"):
            video_name = os.path.splitext(os.path.basename(xml_file))[0]
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # 프레임 번호별 액션 이름을 저장할 딕셔너리
                frame_to_action = {}
                
                for obj in root.findall('object'):
                    for action in obj.findall('action'):
                        action_name = action.find('actionname').text
                        if action_name not in self.class_map:
                            continue
                        
                        class_idx = self.class_map[action_name]
                        
                        for frame_range in action.findall('frame'):
                            start_frame = int(frame_range.find('start').text)
                            end_frame = int(frame_range.find('end').text)
                            
                            for i in range(start_frame, end_frame + 1):
                                # XML은 1-based, 코드는 0-based 이므로 -1
                                frame_to_action[i - 1] = class_idx
                
                if frame_to_action:
                    annotations[video_name] = frame_to_action
            except ET.ParseError:
                print(f"Warning: Could not parse XML file {xml_file}")
                continue
        return annotations

    def _create_samples(self):
        samples = []
        print("Creating training samples...")
        for video_name, frame_to_action in tqdm(self.annotations.items(), desc="Creating Samples"):
            video_frame_dir = os.path.join(self.frame_root, video_name)
            if not os.path.isdir(video_frame_dir): continue
            
            frame_paths = sorted(glob.glob(os.path.join(video_frame_dir, '*.jpg')))
            num_frames = len(frame_paths)

            if num_frames < self.sequence_length:
                continue

            for i in range(num_frames - self.sequence_length + 1):
                # 시퀀스의 중심 프레임으로 라벨을 결정
                center_frame_idx = i + self.sequence_length // 2
                
                # 중심 프레임에 해당하는 액션이 있으면 샘플로 추가
                if center_frame_idx in frame_to_action:
                    label = frame_to_action[center_frame_idx]
                    sequence_paths = frame_paths[i:i + self.sequence_length]
                    samples.append((sequence_paths, label))
        return samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        frame_paths, label = self.samples[idx]
        
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
        label_tensor = torch.tensor(label, dtype=torch.long)

        return video_tensor, label_tensor