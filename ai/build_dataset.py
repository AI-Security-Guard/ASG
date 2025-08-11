# build_dataset.py (Final Version with updated paths)

import os
import glob
import shutil
import random
from tqdm import tqdm

try:
    import cv2
except ImportError:
    print("OpenCV is not installed. Please install it using: pip install opencv-python")
    exit()

# ==============================================================================
#                                설정 (사용자 수정)
# ==============================================================================

# 1. 원본 데이터(mp4, xml)가 있는 폴더 경로
SOURCE_DIRECTORY = r"D:\CCTV\CCTV\all\sample"

# 2. 새로 생성할 데이터셋 폴더 경로
OUTPUT_DIRECTORY = r"D:\CCTV\CCTV\sample_dataset"

# 3. 데이터 분할 비율 (전체 합이 1.0이 되어야 함)
TRAIN_RATIO = 0.8
VAL_RATIO = 0.1
TEST_RATIO = 0.1

# 4. 리사이즈할 해상도 (FHD)
TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080
# ==============================================================================


def create_dirs(base_path):
    """필요한 모든 디렉토리를 생성하는 함수"""
    splits = ['train', 'val', 'test']
    for split in splits:
        os.makedirs(os.path.join(base_path, split, 'frames'), exist_ok=True)
        os.makedirs(os.path.join(base_path, split, 'labels'), exist_ok=True)
    print(f"Directory structure created at: {base_path}")


def extract_resize_and_save_frames(video_path, output_frames_dir):
    """
    비디오에서 프레임을 읽어, 메모리에서 리사이즈한 후, 바로 디스크에 저장하는 함수
    """
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    video_output_folder = os.path.join(output_frames_dir, video_name)
    os.makedirs(video_output_folder, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 메모리 상에서 프레임 리사이즈
        resized_frame = cv2.resize(frame, (TARGET_WIDTH, TARGET_HEIGHT), interpolation=cv2.INTER_AREA)
        
        # 리사이즈된 프레임을 저장
        frame_filename = f"frame_{frame_count:05d}.jpg"
        cv2.imwrite(os.path.join(video_output_folder, frame_filename), resized_frame)
        frame_count += 1
        
    cap.release()
    return frame_count


def build_dataset():
    """메인 데이터셋 구축 함수"""
    print("Starting dataset build process...")
    
    # 1. 디렉토리 구조 생성
    create_dirs(OUTPUT_DIRECTORY)
    
    # 2. 소스 디렉토리에서 mp4와 xml 파일 쌍 찾기
    all_video_files = glob.glob(os.path.join(SOURCE_DIRECTORY, '*.mp4'))
    file_pairs = []
    print(f"Found {len(all_video_files)} video files. Verifying XML pairs...")
    
    for video_path in tqdm(all_video_files, desc="Finding file pairs"):
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        xml_path = os.path.join(SOURCE_DIRECTORY, f"{video_name}.xml")
        if os.path.exists(xml_path):
            file_pairs.append({'video': video_path, 'xml': xml_path})
        else:
            print(f"Warning: XML file not found for {video_path}")
            
    print(f"Found {len(file_pairs)} matched video-xml pairs.")
    
    # 3. 데이터 분할
    random.shuffle(file_pairs)
    
    total_files = len(file_pairs)
    train_end = int(total_files * TRAIN_RATIO)
    val_end = train_end + int(total_files * VAL_RATIO)
    
    train_files = file_pairs[:train_end]
    val_files = file_pairs[train_end:val_end]
    test_files = file_pairs[val_end:]
    
    print(f"Splitting data: {len(train_files)} train, {len(val_files)} val, {len(test_files)} test.")
    
    # 4. 파일 처리 및 복사/추출
    splits = {'train': train_files, 'val': val_files, 'test': test_files}
    
    for split_name, files in splits.items():
        print(f"\nProcessing {split_name} set...")
        output_split_labels_dir = os.path.join(OUTPUT_DIRECTORY, split_name, 'labels')
        output_split_frames_dir = os.path.join(OUTPUT_DIRECTORY, split_name, 'frames')
        
        for pair in tqdm(files, desc=f"Processing {split_name} files"):
            # a. XML 파일 복사 (XML은 원본 그대로 사용)
            shutil.copy(pair['xml'], output_split_labels_dir)
            
            # b. 비디오 프레임 추출 및 리사이즈 후 저장
            extract_resize_and_save_frames(pair['video'], output_split_frames_dir)
            
    print("\nDataset build process completed successfully!")


if __name__ == '__main__':
    if abs(TRAIN_RATIO + VAL_RATIO + TEST_RATIO - 1.0) > 1e-5:
        print("Error: The sum of ratios must be 1.0")
    else:
        build_dataset()