# nnUNetv2 Docker Image
### TL;DR
- This branch is for running nnUNetv2 on SOL2
- dockerdex.umcn.nl:5005/nielsrocholl/nnunetv2:latest
- Run nnUNet commands directly; the entrypoint copies data from storage to the compute node automatically

This is a dockerized version of the nnUnetv2 framework for running on SOL. It handles copying the raw/processed data from storage to the compute node and configures environmental variables. See the [official docs] for how to run nnUnetv2 on a new dataset. See also the documentation on the [nnUNetv1 docker] on which this wrapper is based.

**Do not use `--no-container-entrypoint`**; the entrypoint copies data from storage to the compute node before running nnUNet.

#### Example SOL-2 sbatch script:
```
#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-gpu=11G
#SBATCH --time=07-00:00:00
#SBATCH --container-mounts=<path to nnUNet_raw/preprocessed/results>:/nnunet_data
#SBATCH --container-image="dockerdex.umcn.nl:5005/nielsrocholl/nnunetv2:latest"

nnUNetv2_plan_and_preprocess -d 10 --verify_dataset_integrity
# or: nnUNetv2_train -d 10 3d_fullres 0 --npz --c
```

#### What you probably want to do:
- **nnUNetv2_plan_and_preprocess** -d DATASET_ID --verify_dataset_integrity
  - Can be run for multiple datasets at once. Doesn't require a GPU.
- For each fold: **nnUNetv2_train** -d DATASET_ID MODEL FOLD --npz **--c**
  - Important: use **--c** here so it continues training from checkpoint if your job gets rescheduled.
- After training all folds/models: **nnUNetv2_find_best_configuration** _DATASET_NAME_OR_ID -c CONFIGURATIONS
- **nnUNetv2_predict** -i INPUT_FOLDER -o OUTPUT_FOLDER -d DATASET_NAME_OR_ID -c CONFIGURATION --save_probabilities
- **nnUNetv2_apply_postprocessing** -i FOLDER_WITH_PREDICTIONS -o OUTPUT_FOLDER --pp_pkl_file POSTPROCESSING_FILE -plans_json PLANS_FILE -dataset_json DATASET_JSON_FILE
  
[official docs]: <https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/how_to_use_nnunet.md>
[nnUNetv1 docker]: <https://github.com/DIAGNijmegen/diag-nnunet>
# nnUNet-v2-pro-sol-docker
# nnUNet-v2-pro-sol-docker
