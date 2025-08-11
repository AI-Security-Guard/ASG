# core/model.py (Final Classification Version)

import torch
import torch.nn as nn
from backbones_3d import resnet

class YOWO(nn.Module):
    def __init__(self, cfg):
        super(YOWO, self).__init__()
        
        self.backbone_3d = resnet.resnet18(shortcut_type='A')
        
        # ResNet-18의 마지막 레이어 입력 피처 수는 512
        # backbones_3d/resnet.py 구조에 따라 'fc' 대신 'classifier' 일 수 있음
        # getattr을 사용해 유연하게 대처
        if hasattr(self.backbone_3d, 'fc'):
            num_ch_3d = self.backbone_3d.fc.in_features
        elif hasattr(self.backbone_3d, 'classifier'):
             num_ch_3d = self.backbone_3d.classifier.in_features
        else:
            # 마지막 레이어를 직접 확인해야 함
            # 예시: resnet의 마지막 블록의 출력 채널 확인
            num_ch_3d = 512 

        self.avgpool = nn.AdaptiveAvgPool3d((1, 1, 1))
        
        # 최종 출력 뉴런 수는 cfg 파일에 정의된 클래스 개수
        self.classifier = nn.Linear(num_ch_3d, cfg.MODEL.NUM_CLASSES)

    def forward(self, input):
        x = input.permute(0, 2, 1, 3, 4)

        x = self.backbone_3d.conv1(x)
        x = self.backbone_3d.bn1(x)
        x = self.backbone_3d.relu(x)
        x = self.backbone_3d.maxpool(x)

        x = self.backbone_3d.layer1(x)
        x = self.backbone_3d.layer2(x)
        x = self.backbone_3d.layer3(x)
        x = self.backbone_3d.layer4(x)
        
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        out = self.classifier(x)

        return out