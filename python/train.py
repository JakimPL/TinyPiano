import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm

BATCH_SIZE = 1024
LEARNING_RATE = 1e-2
EPOCHS = 20
T = 64
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def flatten_dataset(ds, time_grid: np.ndarray):
    inputs, targets = [], []
    for pitch, velocity, harmonic, amplitudes in tqdm(ds, desc="Flattening dataset"):
        for i, t in enumerate(time_grid):
            inputs.append((pitch, velocity, harmonic, t))
            targets.append(amplitudes[i])
    return inputs, targets


def collate_batch(inputs, targets):
    pitch = torch.tensor([x[0] for x in inputs], dtype=torch.float32)
    velocity = torch.tensor([x[1] for x in inputs], dtype=torch.float32)
    harmonic = torch.tensor([x[2] for x in inputs], dtype=torch.float32)
    time = torch.tensor([x[3] for x in inputs], dtype=torch.float32)
    target = torch.tensor(targets, dtype=torch.float32)
    return pitch, velocity, harmonic, time, target


def loss_rmse(y_pred: torch.Tensor, y_true: torch.Tensor) -> torch.Tensor:
    """
    Root Mean Squared Error (RMSE) between predicted and true amplitudes.

    Args:
        y_pred: predicted tensor of shape (B, T)
        y_true: target tensor of shape (B, T)

    Returns:
        Scalar RMSE loss
    """
    return torch.sqrt(F.mse_loss(y_pred, y_true) + 1e-9)


def loss_mssl(
        y_pred: torch.Tensor,  # (B, T)
        y_true: torch.Tensor,  # (B, T)
        fft_sizes=(64, 128, 256),
        hop_size_factor: float = 0.25,
        window_fn=torch.hann_window,
) -> torch.Tensor:
    """
    Multi-Scale Spectral Loss (MSSL) for time-domain signals.

    Args:
        y_pred: predicted waveform tensor of shape (B, T)
        y_true: target waveform tensor of shape (B, T)
        fft_sizes: tuple of FFT sizes to compute STFTs at multiple scales
        hop_size_factor: hop length as a fraction of FFT size
        window_fn: torch window function (default: hann)

    Returns:
        Scalar loss (average over all FFT scales)
    """
    device = y_pred.device
    loss = 0.0

    for fft_size in fft_sizes:
        hop_length = int(fft_size * hop_size_factor)
        win = window_fn(fft_size).to(device)

        def stft_mag(x):
            return torch.stft(x, n_fft=fft_size, hop_length=hop_length,
                              window=win, return_complex=True).abs()

        x_mag = stft_mag(y_pred)
        y_mag = stft_mag(y_true)

        x_log = torch.log1p(x_mag)
        y_log = torch.log1p(y_mag)

        loss += F.mse_loss(x_log, y_log)

    return loss / len(fft_sizes)


def loss_function(
        y_pred: torch.Tensor,
        y_true: torch.Tensor,
        alpha: float = 0.1,
        fft_sizes=(64, 128, 256),
        hop_size_factor: float = 0.25,
        window_fn=torch.hann_window,
) -> torch.Tensor:
    """
    Combined loss: alpha * RMSE + (1 - alpha) * MSSL

    Args:
        y_pred: predicted waveform tensor of shape (B, T)
        y_true: target waveform tensor of shape (B, T)
        alpha: weighting factor for RMSE (default: 0.5)
        fft_sizes: FFT sizes for MSSL
        hop_size_factor: hop length as fraction of FFT size
        window_fn: window function for STFT

    Returns:
        Scalar combined loss
    """
    rmse = loss_rmse(y_pred, y_true)
    mssl = loss_mssl(y_pred, y_true, fft_sizes, hop_size_factor, window_fn)
    return alpha * rmse + (1.0 - alpha) * mssl


def add_jitter(x: torch.Tensor, std: float = 1e-3) -> torch.Tensor:
    if not x.requires_grad:  # optional: avoid during eval
        return x
    return x + torch.randn_like(x) * std


def train_model(model, train_loader, loss_fn, optimizer, device, epochs,
                vel_jitter_std=1e-3, time_jitter_std=5e-3):
    model.train()
    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        for b_pitch, b_vel, b_harm, b_time, b_target in tqdm(train_loader, desc=f"Epoch {epoch:02d}"):
            b_pitch = b_pitch.to(device)
            b_vel = b_vel.to(device)
            b_harm = b_harm.to(device)
            b_time = b_time.to(device)
            b_target = b_target.to(device)

            # ✅ Apply jitter to continuous inputs
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


def evaluate_model(model, dataset, time_grid, device):
    model.eval()
    harmonic_errors = []

    with torch.no_grad():
        for item in tqdm(dataset, desc="Evaluating"):
            pitch = item["pitch"]
            velocity = item["velocity"]
            harmonic = item["harmonic"]
            true = np.exp(item["amplitudes"])

            t_array = torch.tensor(time_grid, dtype=torch.float32, device=device)
            p_tensor = torch.full_like(t_array, pitch, dtype=torch.float32)
            v_tensor = torch.full_like(t_array, float(velocity), dtype=torch.float32)
            h_tensor = torch.full_like(t_array, harmonic, dtype=torch.float32)

            pred = model(p_tensor, v_tensor, h_tensor, t_array).cpu().numpy()
            err = loss_function(pred, true)
            harmonic_errors.append(err)

    mean_err = np.mean(harmonic_errors)
    print(f"✅ L2-normalized RMSE (per harmonic): {mean_err:.6f}")
    return mean_err
