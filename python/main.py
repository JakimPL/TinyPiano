import argparse
from pathlib import Path
from typing import Tuple, Union

from constants import DATASET_PATH, ARCHIVE_PATH, MODEL_PATH
from dataset import build_archive_from_files, HarmonicsArchive
from train import HIDDEN_SIZES, EPOCHS, BATCH_SIZE, LEARNING_RATE
from train import train_and_save


def parse_hidden_sizes(hidden_sizes: str) -> Tuple[int, int, int]:
    sizes = tuple(map(int, hidden_sizes.split(',')))
    if len(sizes) != 3 or any(size <= 0 for size in sizes):
        raise ValueError("Hidden sizes must be exactly 3 positive integers separated by commas (e.g., '8,8,4').")

    return sizes


def build_archive(
        dataset_path: Union[str, Path] = DATASET_PATH,
        archive_path: Union[str, Path] = ARCHIVE_PATH
) -> None:
    dataset_path = Path(dataset_path)
    archive_path = Path(archive_path)
    archive = build_archive_from_files(dataset_path)
    archive.save(archive_path)


def train(
        archive: HarmonicsArchive,
        hidden_sizes: Tuple[int, ...] = HIDDEN_SIZES,
        epochs: int = EPOCHS,
        batch_size: int = BATCH_SIZE,
        learning_rate: float = LEARNING_RATE,
        model_path: Union[str, Path] = MODEL_PATH
):
    model_path = Path(model_path)
    train_and_save(archive, hidden_sizes, epochs, batch_size, learning_rate, model_path)


def main():
    parser = argparse.ArgumentParser(description="Harmonic Model Training Script")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build the dataset archive")
    build_parser.add_argument(
        "--dataset-path", type=str, default=DATASET_PATH,
        help="Path to the dataset directory (default: %(default)s)"
    )
    build_parser.add_argument(
        "--archive-path", type=str, default=ARCHIVE_PATH,
        help="Path to save the archive file (default: %(default)s)"
    )

    train_parser = subparsers.add_parser("train", help="Train the model")
    train_parser.add_argument(
        "--archive-path", type=str, default=ARCHIVE_PATH,
        help="Path to the archive file (default: %(default)s)"
    )
    train_parser.add_argument(
        "--hidden-sizes", type=parse_hidden_sizes, default="64,64,32",
        help="Comma-separated hidden layer sizes (default: %(default)s)"
    )
    train_parser.add_argument(
        "--epochs", type=int, default=EPOCHS,
        help="Number of training epochs (default: %(default)s)"
    )
    train_parser.add_argument(
        "--batch-size", type=int, default=BATCH_SIZE,
        help="Batch size for training (default: %(default)s)"
    )
    train_parser.add_argument(
        "--learning-rate", type=float, default=LEARNING_RATE,
        help="Learning rate for the optimizer (default: %(default)s)"
    )
    train_parser.add_argument(
        "--model-path", type=str, default=MODEL_PATH,
        help="Path to save the trained model (default: %(default)s)"
    )

    args = parser.parse_args()

    if args.command == "build":
        build_archive(args.dataset_path, args.archive_path)
    elif args.command == "train":
        archive = HarmonicsArchive.load(args.archive_path)
        train(
            archive,
            hidden_sizes=args.hidden_sizes,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            model_path=args.model_path
        )


if __name__ == "__main__":
    main()
