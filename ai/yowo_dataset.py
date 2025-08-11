# yowo_dataset.py (Final Version with 1-based to 0-based fix)

import os
import glob
import torch
from torch.utils.data import Dataset
from PIL import Image
import numpy as np
import xml.etree.ElementTree as ET
from tqdm import tqdm

class YOWODataset(Dataset):
    def __init__(self, root_dir, split='train', sequence_length=16, transform=None, img_size=(224, 224), max_objs=10):
        self.sequence_length = sequence_length
        self.transform = transform
        self.img_size = img_size
        self.max_objs = max_objs
        
        self.label_root = os.path.join(root_dir, split, 'labels')
        self.frame_root = os.path.join(root_dir, split, 'frames')
        
        if not os.path.isdir(self.label_root):
            raise ValueError(f"Labels directory not found at: {self.label_root}")

        self.xml_files = sorted(glob.glob(os.path.join(self.label_root, '*.xml')))
        
        self.annotations = self._parse_all_annotations()
        self.samples = self._create_samples()

    def _parse_all_annotations(self):
        annotations = {}
        print("Parsing XML annotations...")
        for xml_file in tqdm(self.xml_files, desc="Parsing XMLs"):
            video_name = os.path.splitext(os.path.basename(xml_file))[0]
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                video_annotations = {}
                size_node = root.find('size')
                if size_node is None: continue
                
                img_width_node = size_node.find('width')
                img_height_node = size_node.find('height')
                if img_width_node is None or img_height_node is None: continue

                img_width = int(img_width_node.text)
                img_height = int(img_height_node.text)

                class_map = {'assault': 0}

                for track in root.findall('track'):
                    label = track.get('label')
                    if label not in class_map:
                        continue
                    
                    class_idx = class_map[label]

                    for box in track.findall('box'):
                        # [수정] XML의 1-based 프레임 번호를 0-based 인덱스로 변환하기 위해 1을 뺍니다.
                        frame_idx = int(box.get('frame')) - 1
                        
                        xtl = float(box.get('xtl'))
                        ytl = float(box.get('ytl'))
                        xbr = float(box.get('xbr'))
                        ybr = float(box.get('ybr'))
                        
                        x_center = (xtl + xbr) / 2 / img_width
                        y_center = (ytl + ybr) / 2 / img_height
                        width = (xbr - xtl) / img_width
                        height = (ybr - ytl) / img_height

                        if frame_idx not in video_annotations:
                            video_annotations[frame_idx] = []
                        video_annotations[frame_idx].append([class_idx, x_center, y_center, width, height])
                
                if video_annotations: # 어노테이션이 있는 경우에만 추가
                    annotations[video_name] = video_annotations
            except ET.ParseError:
                print(f"Warning: Could not parse XML file {xml_file}")
                continue
        return annotations

    def _create_samples(self):
        samples = []
        print("Creating training samples...")
        if not self.annotations:
            print("Warning: No valid annotations found after parsing. Cannot create samples.")
            return samples

        for video_name, video_annotations in tqdm(self.annotations.items(), desc="Creating Samples"):
            video_frame_dir = os.path.join(self.frame_root, video_name)
            if not os.path.isdir(video_frame_dir): continue
            
            frame_paths = sorted(glob.glob(os.path.join(video_frame_dir, '*.jpg')))
            num_frames = len(frame_paths)

            if num_frames < self.sequence_length:
                continue

            for i in range(num_frames - self.sequence_length + 1):
                has_annotation = False
                for frame_idx_offset in range(self.sequence_length):
                    frame_num = i + frame_idx_offset # 0-based index
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

        target = torch.zeros((self.max_objs, 5))
        last_frame_idx = start_frame + self.sequence_length - 1
        
        if video_name in self.annotations and last_frame_idx in self.annotations[video_name]:
            boxes = self.annotations[video_name][last_frame_idx]
            num_boxes = min(len(boxes), self.max_objs)
            for i in range(num_boxes):
                target[i] = torch.tensor(boxes[i])

        return video_tensor, target