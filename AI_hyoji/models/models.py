import torch
import torch.nn as nn
import torch.nn.functional as F

from .backbone import build_backbone
from .token_encoder import build_token_encoder

class DFGAR(nn.Module):
    def __init__(self, args):
        super().__init__()

        self.num_class = args.num_activities
        self.num_frame = args.num_frame
        self.hidden_dim = args.hidden_dim
        self.num_tokens = args.num_tokens

        self.backbone = build_backbone(args)
        self.token_encoder = build_token_encoder(args)

        self.query_embed = nn.Embedding(self.num_tokens, self.hidden_dim)
        self.input_proj = nn.Conv2d(self.backbone.num_channels, self.token_encoder.d_model, kernel_size=1)

        self.conv1 = nn.Conv1d(self.hidden_dim, self.hidden_dim, kernel_size=5)
        self.conv2 = nn.Conv1d(self.hidden_dim, self.hidden_dim, kernel_size=5)
        self.conv3 = nn.Conv1d(self.hidden_dim, self.hidden_dim, kernel_size=5)

        self.self_attn = nn.MultiheadAttention(self.token_encoder.d_model, args.nheads_agg, dropout=args.drop_rate)

        self.dropout1 = nn.Dropout(args.drop_rate)
        self.norm1 = nn.LayerNorm(self.hidden_dim)
        self.norm2 = nn.LayerNorm(self.hidden_dim)
        self.classifier = nn.Linear(self.hidden_dim, self.num_class)

        self.relu = F.relu

        for name, m in self.named_modules():
            if 'backbone' not in name and 'token_encoder' not in name:
                if isinstance(m, nn.Linear):
                    nn.init.kaiming_normal_(m.weight)
                    if m.bias is not None:
                        nn.init.zeros_(m.bias)

    def forward(self, x):
        # x: [B, T, 3, H, W]
        B, T, C, H, W = x.shape
        x = x.view(B * T, C, H, W)

        src, pos = self.backbone(x)               # [B*T, C, H', W']
        src = self.input_proj(src)                # [B*T, D, H', W']
        tokens, _ = self.token_encoder(src, None, self.query_embed.weight, pos)
        tokens = tokens.view(B, T, self.num_tokens, -1)  # [B, T, K, D]

        tokens = tokens.permute(0, 2, 3, 1).contiguous()     # [B, K, D, T]
        tokens = tokens.view(B * self.num_tokens, -1, T)     # [B*K, D, T]

        tokens = self.relu(self.conv1(tokens))
        tokens = self.relu(self.conv2(tokens))
        tokens = self.relu(self.conv3(tokens))
        tokens = tokens.mean(dim=2)                          # [B*K, D]
        tokens = self.norm1(tokens)

        tokens = tokens.view(B, self.num_tokens, -1).permute(1, 0, 2).contiguous()  # [K, B, D]
        attn_out, _ = self.self_attn(tokens, tokens, tokens)
        tokens = tokens + self.dropout1(attn_out)
        tokens = self.norm2(tokens)

        tokens = tokens.permute(1, 0, 2).contiguous()  # [B, K, D]
        pooled = tokens.mean(dim=1)                    # [B, D]
        logits = self.classifier(pooled)               # [B, num_class]

        return logits
