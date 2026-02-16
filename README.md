# nnUNetv2 Docker for SOL

Docker image for running [nnUNet-v2-pro](https://github.com/nielsRocholl/nnUNet-v2-pro) on the SOL HPC cluster.

**Image:** `dockerdex.umcn.nl:5005/nielsrocholl/nnunet-v2-pro-sol-docker:latest`

---

## What it does

- Runs nnUNet-v2-pro (enhanced nnUNet with WandB, ROI prompting, etc.)
- **Training only:** Copies preprocessed data from storage to the compute node for fast I/O, writes results to storage, removes the copy when done
- **All other commands** (plan/preprocess, predict, etc.): Use storage directly

---

## How it works

| Command | Data location | Notes |
|---------|---------------|------|
| `nnUNetv2_train` | Preprocessed copied to compute; results written to storage | Copy is removed after successful training |
| `nnUNetv2_plan_and_preprocess`, `nnUNetv2_predict`, etc. | Storage only | No copy, reads/writes directly on mounted storage |

The container entrypoint intercepts nnUNet commands. For training it copies data, runs training, then cleans up. For everything else it runs the command as-is.

---

## How to use it

### 1. Mount your data

Your folder must contain `nnUNet_raw`, `nnUNet_preprocessed`, and `nnUNet_results` (the last two are created by nnUNet if missing):

```
/your/path/
├── nnUNet_raw/
├── nnUNet_preprocessed/
└── nnUNet_results/
```

Mount it to `/nnunet_data`:

```
--container-mounts=/your/path/:/nnunet_data
```

### 2. Run nnUNet commands

Do **not** use `--no-container-entrypoint`. Run commands as usual:

```bash
# Preprocessing (uses storage)
nnUNetv2_plan_and_preprocess -d 10 --verify_dataset_integrity

# Training (copies preprocessed to compute, writes results to storage)
nnUNetv2_train -d 10 3d_fullres 0 --npz --c

# Prediction (uses storage)
nnUNetv2_predict -i INPUT -o OUTPUT -d 10 -c 3d_fullres
```

### 3. Tuning the copy (training only)

Training copies preprocessed data to the compute node before running. Tune parallelism with env vars (set in your sbatch script or session):

| Variable | Meaning | Default |
|----------|---------|---------|
| `NNUNET_COPY_TRANSFERS` | Parallel file transfers | 16 |
| `NNUNET_COPY_STREAMS` | Threads per transfer | 16 |

Example for a node with many CPUs:
```bash
export NNUNET_COPY_TRANSFERS=32
export NNUNET_COPY_STREAMS=32
nnUNetv2_train -d 10 3d_fullres 0 --npz --c
```

If rclone fails, the wrapper falls back to the built-in copy (slower).

### 4. Example sbatch script

```bash
#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-gpu=11G
#SBATCH --time=07-00:00:00
#SBATCH --container-mounts=/path/to/your/nnunet_data/:/nnunet_data
#SBATCH --container-image="dockerdex.umcn.nl:5005/nielsrocholl/nnunet-v2-pro-sol-docker:latest"

nnUNetv2_plan_and_preprocess -d 10 --verify_dataset_integrity
# or: nnUNetv2_train -d 10 3d_fullres 0 --npz --c
```

---

## Typical workflow

1. **Plan and preprocess:** `nnUNetv2_plan_and_preprocess -d DATASET_ID --verify_dataset_integrity` (no GPU)
2. **Train each fold:** `nnUNetv2_train -d DATASET_ID 3d_fullres FOLD --npz --c` (use `--c` to resume)
3. **Find best config:** `nnUNetv2_find_best_configuration DATASET_ID -c CONFIGURATIONS`
4. **Predict:** `nnUNetv2_predict -i INPUT -o OUTPUT -d DATASET_ID -c CONFIG`

See [nnUNet docs](https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/how_to_use_nnunet.md) and [nnUNet-v2-pro](https://github.com/nielsRocholl/nnUNet-v2-pro) for details.
