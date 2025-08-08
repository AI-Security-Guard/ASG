# core/model.py

import torch
import torch.nn as nn

from backbones_2d import darknet
from backbones_3d import resnet
from core.cfam import CFAMBlock

class YOWO(nn.Module):
    def __init__(self, cfg):
        super(YOWO, self).__init__()
        self.cfg = cfg

        # ----------------- 2D Backbone -----------------
        if cfg.MODEL.BACKBONE_2D == "darknet":
            self.backbone_2d = darknet.Darknet("cfg/yolo.cfg")
            # YOLO의 마지막 레이어 출력 채널 수는 1024
            num_ch_2d = 1024 
        else:
            raise ValueError(f"2D backbone {cfg.MODEL.BACKBONE_2D} not supported.")

        # ----------------- 3D Backbone -----------------
        if cfg.MODEL.BACKBONE_3D == "resnet18":
            self.backbone_3d = resnet.resnet18(shortcut_type='A')
            # ResNet-18의 마지막 레이어 입력 피처 수는 512
            num_ch_3d = 512 
        else:
            raise ValueError(f"3D backbone {cfg.MODEL.BACKBONE_3D} not supported.")
        
        # ----------------- Aggregation-Fusion -----------------
        self.cfam = CFAMBlock(num_ch_2d + num_ch_3d, 1024)
        
        # ----------------- Prediction Head -----------------
        # num_anchors * (num_classes + 1_obj_conf + 4_coords)
        num_anchors = 5 
        num_preds = num_anchors * (cfg.MODEL.NUM_CLASSES + 5)
        self.conv_final = nn.Conv2d(1024, num_preds, kernel_size=1, bias=False)

    def forward(self, input):
        # ----------------- 3D Feature Extraction -----------------
        # Input: [B, T, C, H, W]
        # 3D CNN은 [B, C, T, H, W]를 기대하므로 permute
        x_3d = input.permute(0, 2, 1, 3, 4)
        
        # ResNet의 feature extractor 부분만 통과
        x_3d = self.backbone_3d.conv1(x_3d)
        x_3d = self.backbone_3d.bn1(x_3d)
        x_3d = self.backbone_3d.relu(x_3d)
        x_3d = self.backbone_3d.maxpool(x_3d)

        x_3d = self.backbone_3d.layer1(x_3d)
        x_3d = self.backbone_3d.layer2(x_3d)
        x_3d = self.backbone_3d.layer3(x_3d)
        x_3d = self.backbone_3d.layer4(x_3d)
        
        # [B, C, T, H, W] -> [B, C, H, W] (시간 차원 squeeze)
        x_3d = torch.squeeze(x_3d, dim=2)
        
        # ----------------- 2D Feature Extraction -----------------
        # 비디오 클립의 마지막 프레임만 사용
        x_2d = input[:, -1, :, :, :] # [B, C, H, W]
        x_2d = self.backbone_2d(x_2d)

        # ----------------- Feature Fusion & Prediction -----------------
        # 채널 차원을 기준으로 두 피처를 연결
        x = torch.cat((x_3d, x_2d), dim=1)
        x = self.cfam(x)
        
        out = self.conv_final(x)

        return out