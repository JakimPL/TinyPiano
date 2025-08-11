import torch
import torch.nn as nn

from constants import MAX_HARMONICS


class DirectTinyHarmonicModel(nn.Module):
    def __init__(
            self,
            num_harmonics: int = MAX_HARMONICS,
            hidden_sizes: tuple = (64, 64, 32),
            activation=nn.SiLU
    ):
        super().__init__()
        self.num_harmonics = num_harmonics

        layers = []
        input_dim = 4  # pitch, velocity, harmonic, time

        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(input_dim, hidden_size))
            layers.append(activation())
            input_dim = hidden_size

        layers.append(nn.Linear(input_dim, 1))

        self.mlp = nn.Sequential(*layers)

    def forward(
            self,
            pitch: torch.FloatTensor,  # (B,)
            velocity: torch.FloatTensor,  # (B,)
            harmonic: torch.FloatTensor,  # (B,)
            time: torch.FloatTensor  # (B,)
    ) -> torch.FloatTensor:  # (B,)
        if pitch.dim() == 1:
            pitch = pitch.unsqueeze(1)
        if velocity.dim() == 1:
            velocity = velocity.unsqueeze(1)
        if harmonic.dim() == 1:
            harmonic = harmonic.unsqueeze(1)
        if time.dim() == 1:
            time = time.unsqueeze(1)

        x = torch.cat([pitch, velocity, harmonic, time], dim=1)  # (B, 4)
        log_amp = self.mlp(x).squeeze(1)  # (B,)
        return log_amp
