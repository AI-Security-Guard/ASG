import torch
from models.models import DFGAR as DFWSGARModel

def get_model_and_args():
    args = type('', (), {})()
    args.num_activities = 2
    args.num_frame = 18
    args.hidden_dim = 256
    args.num_tokens = 6
    args.nheads_agg = 4
    args.drop_rate = 0.1
    args.position_embedding = 'sine'
    args.dilation = False
    args.nheads = 8
    args.ffn_dim = 512
    args.enc_layers = 1
    args.pre_norm = False
    args.backbone = 'resnet18'
    args.motion = True
    args.motion_layer = 3
    args.multi_corr = True
    args.corr_dim = 64
    args.neighbor_size = 2

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DFWSGARModel(args).to(device)
    model.load_state_dict(torch.load("model/model.pth", map_location=device))
    model.eval()

    return model, args, device