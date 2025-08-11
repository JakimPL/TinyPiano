from pathlib import Path
from typing import List, Tuple, Union

import numpy as np
import torch
import torch.nn.functional as F
from torch import Tensor
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm

from constants import MODEL_PATH
from dataset import HarmonicTorchDataset, HarmonicsArchive
from model import DirectTinyHarmonicModel

# Default training parameters
HIDDEN_SIZES = (64, 64, 32)
BATCH_SIZE = 1024
LEARNING_RATE = 1e-2
EPOCHS = 20
T = 64


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def flatten_dataset(ds: HarmonicTorchDataset, time_grid: np.ndarray) -> Tuple[List[Tuple[float, float, float, float]], List[float]]:
    inputs, targets = [], []
    for pitch, velocity, harmonic, amplitudes in tqdm(ds, desc="Flattening dataset"):
        for i, t in enumerate(time_grid):
            inputs.append((pitch, velocity, harmonic, t))
            targets.append(amplitudes[i])
    return inputs, targets


def collate_batch(inputs: List[Tuple[float, float, float, float]], targets: List[float]) -> Tuple[Tensor, Tensor, Tensor, Tensor, Tensor]:
    pitch = torch.tensor([x[0] for x in inputs], dtype=torch.float32)
    velocity = torch.tensor([x[1] for x in inputs], dtype=torch.float32)
    harmonic = torch.tensor([x[2] for x in inputs], dtype=torch.float32)
    time = torch.tensor([x[3] for x in inputs], dtype=torch.float32)
    target = torch.tensor(targets, dtype=torch.float32)
    return pitch, velocity, harmonic, time, target


def loss_rmse(y_pred: Tensor, y_true: Tensor) -> Tensor:
    return torch.sqrt(F.mse_loss(y_pred, y_true) + 1e-9)


def loss_mssl(
        y_pred: Tensor,
        y_true: Tensor,
        fft_sizes: Tuple[int, ...] = (64, 128, 256),
        hop_size_factor: float = 0.25,
        window_fn: callable = torch.hann_window,
) -> Tensor:
    device = y_pred.device
    loss = 0.0

    for fft_size in fft_sizes:
        hop_length = int(fft_size * hop_size_factor)
        win = window_fn(fft_size).to(device)

        def stft_mag(x: Tensor) -> Tensor:
            return torch.stft(
                x, n_fft=fft_size, hop_length=hop_length,
                window=win, return_complex=True
            ).abs()

        x_mag = stft_mag(y_pred)
        y_mag = stft_mag(y_true)

        x_log = torch.log1p(x_mag)
        y_log = torch.log1p(y_mag)

        loss += F.mse_loss(x_log, y_log)

    return loss / len(fft_sizes)


def loss_function(
        y_pred: Tensor,
        y_true: Tensor,
        alpha: float = 0.1,
        fft_sizes: Tuple[int, ...] = (64, 128, 256),
        hop_size_factor: float = 0.25,
        window_fn: callable = torch.hann_window,
) -> Tensor:
    rmse = loss_rmse(y_pred, y_true)
    mssl = loss_mssl(y_pred, y_true, fft_sizes, hop_size_factor, window_fn)
    return alpha * rmse + (1.0 - alpha) * mssl


def add_jitter(x: Tensor, std: float = 1e-3) -> Tensor:
    if not x.requires_grad:  # optional: avoid during eval
        return x
    return x + torch.randn_like(x) * std


def train_model(
        model: DirectTinyHarmonicModel,
        train_loader: DataLoader,
        loss_fn: callable,
        optimizer: torch.optim.Optimizer,
        device: torch.device,
        epochs: int,
        vel_jitter_std: float = 1e-3,
        time_jitter_std: float = 5e-3
) -> None:
    model.train()
    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        for b_pitch, b_vel, b_harm, b_time, b_target in tqdm(train_loader, desc=f"Epoch {epoch}/{epochs}"):
            b_pitch = b_pitch.to(device)
            b_vel = b_vel.to(device)
            b_harm = b_harm.to(device)
            b_time = b_time.to(device)
            b_target = b_target.to(device)

            # Apply jitter
            b_vel_j = add_jitter(b_vel, std=vel_jitter_std)
            b_time_j = add_jitter(b_time, std=time_jitter_std)

            optimizer.zero_grad()
            out = model(b_pitch, b_vel_j, b_harm, b_time_j)
            loss = loss_fn(out, b_target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * b_pitch.size(0)

        avg_loss = total_loss / len(train_loader.dataset)
        print(f"Epoch {epoch:02d} - MSE Loss: {avg_loss:.6f}")


def train_and_save(
        archive: HarmonicsArchive,
        hidden_sizes: Tuple[int, ...] = HIDDEN_SIZES,
        epochs: int = EPOCHS,
        batch_size: int = BATCH_SIZE,
        learning_rate: float = LEARNING_RATE,
        model_path: Union[str, Path] = MODEL_PATH,
) -> DirectTinyHarmonicModel:
    common_times = np.linspace(0.0, 4.0, T, dtype=np.float32)
    dataset = HarmonicTorchDataset(archive, time_grid=common_times, use_log=True, return_torch=False)

    # Flatten data to (p, v, h, t) → amplitude
    flat_inputs, flat_targets = flatten_dataset(dataset, common_times)
    pitch, vel, harm, time, target = collate_batch(flat_inputs, flat_targets)

    # Build dataloader
    train_dataset = TensorDataset(pitch, vel, harm, time, target)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # Initialize model and optimizer
    model = DirectTinyHarmonicModel(hidden_sizes=hidden_sizes).to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = torch.nn.MSELoss()

    # Train
    try:
        train_model(model, train_loader, loss_fn, optimizer, DEVICE, epochs)
    except KeyboardInterrupt:
        print("Training interrupted. Saving current model state...")

    # Save model
    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), model_path)

    return model
