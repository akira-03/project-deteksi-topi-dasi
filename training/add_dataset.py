import argparse
import random
import shutil
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
LABEL_EXTENSIONS = {".txt"}
SPLITS = ("train", "valid", "test")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Add a YOLO dataset into this project's dataset folder."
    )
    parser.add_argument("source", help="Folder or .zip containing images and YOLO labels.")
    parser.add_argument("--dataset", default="dataset", help="Target dataset folder.")
    parser.add_argument(
        "--prefix",
        default="added",
        help="Prefix for copied filenames to avoid name collisions.",
    )
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--valid-ratio", type=float, default=0.1)
    parser.add_argument("--test-ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--max-class-id",
        type=int,
        default=1,
        help="Highest allowed YOLO class id. For topi/dasi this is 1.",
    )
    return parser.parse_args()


def ensure_target_dirs(dataset_dir):
    for split in SPLITS:
        (dataset_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (dataset_dir / "labels" / split).mkdir(parents=True, exist_ok=True)


def extract_if_zip(source):
    source_path = Path(source).resolve()
    if source_path.suffix.lower() != ".zip":
        return source_path, None

    temp_dir = tempfile.TemporaryDirectory(prefix="add_dataset_")
    extract_dir = Path(temp_dir.name)
    with ZipFile(source_path) as archive:
        archive.extractall(extract_dir)
    return extract_dir, temp_dir


def list_images(root):
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]


def list_labels(root):
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in LABEL_EXTENSIONS
    ]


def build_label_index(labels):
    index = {}
    for label in labels:
        index.setdefault(label.stem, []).append(label)
    return index


def common_prefix_score(left, right):
    left_parts = [part.lower() for part in left.parts]
    right_parts = [part.lower() for part in right.parts]
    score = 0
    for left_part, right_part in zip(left_parts, right_parts):
        if left_part != right_part:
            break
        score += 1
    return score


def folder_hint_score(image, label):
    image_parts = [part.lower() for part in image.parts]
    label_parts = [part.lower() for part in label.parts]
    score = 0

    # Common YOLO exports keep images and labels in sibling folders.
    for image_dir in ("images", "image", "imgs", "foto", "photos"):
        if image_dir in image_parts:
            index = image_parts.index(image_dir)
            expected = image_parts[:index] + ["labels"] + image_parts[index + 1 :]
            if expected[:-1] == label_parts[:-1]:
                score += 100

            expected = image_parts[:index] + ["label"] + image_parts[index + 1 :]
            if expected[:-1] == label_parts[:-1]:
                score += 100

    return score


def direct_label_candidates(image):
    candidates = []
    parts = list(image.parts)
    for index, part in enumerate(parts):
        if part.lower() not in {"images", "image", "imgs", "foto", "photos"}:
            continue
        for label_dir in ("labels", "label"):
            candidate_parts = parts[:index] + [label_dir] + parts[index + 1 :]
            candidate = Path(*candidate_parts).with_suffix(".txt")
            candidates.append(candidate)
    return candidates


def find_label_for_image(image, label_index, repeated_image_stems):
    for candidate in direct_label_candidates(image):
        if candidate.exists():
            return candidate

    candidates = label_index.get(image.stem, [])
    if not candidates:
        return None
    if image.stem in repeated_image_stems:
        return None
    if len(candidates) == 1:
        return candidates[0]

    ranked = sorted(
        candidates,
        key=lambda label: (
            folder_hint_score(image, label),
            common_prefix_score(image.parent, label.parent),
        ),
        reverse=True,
    )
    best = ranked[0]
    if folder_hint_score(image, best) <= 0:
        return None
    return best


def split_from_path(path):
    parts = {part.lower() for part in path.parts}
    if "train" in parts:
        return "train"
    if "valid" in parts or "val" in parts:
        return "valid"
    if "test" in parts:
        return "test"
    return None


def validate_label(label_path, max_class_id):
    for line_number, raw_line in enumerate(label_path.read_text().splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 5:
            raise ValueError(
                f"{label_path}: line {line_number} must contain 5 YOLO values"
            )
        try:
            class_id = int(parts[0])
            values = [float(value) for value in parts[1:]]
        except ValueError as exc:
            raise ValueError(f"{label_path}: line {line_number} has invalid numbers") from exc
        if class_id < 0 or class_id > max_class_id:
            raise ValueError(
                f"{label_path}: line {line_number} class id {class_id} is outside 0-{max_class_id}"
            )
        if any(value < 0 or value > 1 for value in values):
            raise ValueError(
                f"{label_path}: line {line_number} box values must be normalized 0-1"
            )


def collect_pairs(source_dir, max_class_id):
    images = list_images(source_dir)
    image_stem_counts = {}
    for image in images:
        image_stem_counts[image.stem] = image_stem_counts.get(image.stem, 0) + 1
    repeated_image_stems = {
        stem for stem, count in image_stem_counts.items() if count > 1
    }
    labels = build_label_index(list_labels(source_dir))
    pairs = []
    missing_labels = []

    for image in images:
        label = find_label_for_image(image, labels, repeated_image_stems)
        if label is None:
            missing_labels.append(image)
            continue
        validate_label(label, max_class_id)
        pairs.append((image, label, split_from_path(image) or split_from_path(label)))

    if not pairs:
        raise ValueError("No matching image/label pairs found.")

    if missing_labels:
        sample = ", ".join(str(path.name) for path in missing_labels[:5])
        print(
            f"Warning: skipped {len(missing_labels)} images without matching labels: {sample}",
            file=sys.stderr,
        )

    return pairs


def assign_splits(pairs, train_ratio, valid_ratio, test_ratio, seed):
    if abs((train_ratio + valid_ratio + test_ratio) - 1.0) > 0.0001:
        raise ValueError("Split ratios must add up to 1.0")

    if all(split is not None for _, _, split in pairs):
        return [(image, label, split) for image, label, split in pairs]

    shuffled = pairs[:]
    random.Random(seed).shuffle(shuffled)
    total = len(shuffled)
    train_end = int(total * train_ratio)
    valid_end = train_end + int(total * valid_ratio)

    assigned = []
    for index, (image, label, split) in enumerate(shuffled):
        if split is None:
            if index < train_end:
                split = "train"
            elif index < valid_end:
                split = "valid"
            else:
                split = "test"
        assigned.append((image, label, split))
    return assigned


def unique_target(base_dir, filename):
    target = base_dir / filename
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    counter = 1
    while True:
        candidate = base_dir / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def copy_pairs(pairs, dataset_dir, prefix):
    counts = {split: 0 for split in SPLITS}
    for image, label, split in pairs:
        if split not in SPLITS:
            raise ValueError(f"Unsupported split '{split}' for {image}")

        new_stem = f"{prefix}_{image.stem}"
        image_target = unique_target(
            dataset_dir / "images" / split, f"{new_stem}{image.suffix.lower()}"
        )
        label_target = dataset_dir / "labels" / split / f"{image_target.stem}.txt"

        shutil.copy2(image, image_target)
        shutil.copy2(label, label_target)
        counts[split] += 1
    return counts


def main():
    args = parse_args()
    dataset_dir = Path(args.dataset).resolve()
    source_dir, temp_dir = extract_if_zip(args.source)

    try:
        ensure_target_dirs(dataset_dir)
        pairs = collect_pairs(source_dir, args.max_class_id)
        assigned = assign_splits(
            pairs,
            args.train_ratio,
            args.valid_ratio,
            args.test_ratio,
            args.seed,
        )
        counts = copy_pairs(assigned, dataset_dir, args.prefix)
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()

    total = sum(counts.values())
    print(f"Added {total} image/label pairs into {dataset_dir}")
    for split in SPLITS:
        print(f"{split}: {counts[split]}")


if __name__ == "__main__":
    main()
