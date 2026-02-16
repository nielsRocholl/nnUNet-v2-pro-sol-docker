#!/usr/local/bin/python3
import argparse
import os
import subprocess
import sys
from pathlib import Path


def wrap_plan_and_preprocess(argv):
    # Import nnunetv2 now environment variables are set
    import nnunetv2.utilities.shutil_sol as shutil_sol
    from nnunetv2.utilities.dataset_name_id_conversion import convert_id_to_dataset_name

    # Copy raw data to compute node
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', nargs='+', type=int,
                        help="[REQUIRED] List of dataset IDs. Example: 2 4 5. This will run fingerprint extraction, experiment "
                             "planning and preprocessing for these datasets. Can of course also be just one dataset")
    args, unrecognized_args = parser.parse_known_args()

    prepdir = Path('/root/nnUNet_raw')

    for d in args.d:
        dataset_name = convert_id_to_dataset_name(d)
        print(f'Copying raw data for dataset {dataset_name} to compute node')
        if not os.path.exists(prepdir / dataset_name):
            prepdir.mkdir(parents=True, exist_ok=True)
            shutil_sol.copytree(Path(os.environ['nnUNet_raw']) / dataset_name, prepdir / dataset_name)

    # New environment variable
    os.environ['nnUNet_raw'] = str(prepdir)
    # Run nnUnetv2 command minus wrapper
    print("Running:", argv)
    subprocess.run(argv, env=os.environ)


def wrap_train(argv):
    # Import nnunetv2 now environment variables are set
    import nnunetv2.utilities.shutil_sol as shutil_sol
    from nnunetv2.utilities.dataset_name_id_conversion import maybe_convert_to_dataset_name

    # Copy processed data to compute node
    parser = argparse.ArgumentParser()
    parser.add_argument('dummy_train', type=str,
                        help="dummy since for training the dataset id is hardcoded to be second arg for some reason")
    parser.add_argument('dataset_name_or_id', type=str,
                        help="Dataset name or ID to train with")
    args, unrecognized_args = parser.parse_known_args()

    prepdir = Path('/root/nnUNet_preprocessed')

    dataset_name = maybe_convert_to_dataset_name(args.dataset_name_or_id)
    print(f'Copying processed data for dataset {dataset_name} to compute node')
    if not os.path.exists(prepdir / dataset_name):
        prepdir.mkdir(parents=True, exist_ok=True)
        shutil_sol.copytree(Path(os.environ['nnUNet_preprocessed']) / dataset_name, prepdir / dataset_name)

    # New environment variable
    os.environ['nnUNet_preprocessed'] = str(prepdir)
    # Run nnUnetv2 command minus wrapper
    print("Running:", argv)
    subprocess.run(argv, env=os.environ)


if __name__ == '__main__':
    actions = {
        'nnUNetv2_plan_and_preprocess': wrap_plan_and_preprocess,
        'nnUNetv2_train': wrap_train
    }

    if len(sys.argv) < 2:
        print("You should probably add some parameters first.")
        sys.exit(1)

    if sys.argv[1] in actions.keys():
        action = actions[sys.argv[1]]
        print(f"Running with {action}")
        # Run wrapper action
        action(sys.argv[1:])
        # We start a new subprocess here since the env vars set above will
        # only be used in a new subprocess and the c-submit script overwrites
        # docker file env vars so that doesn't work. We also need to import
        # nnunetv2 after setting these apparently or it won't find the data.
    else:
        print("Running with unsupported argument, not copying data to compute node first")
        # Just run nnUnetv2 command
        if len(sys.argv) > 1:
            subprocess.run(sys.argv[1:], env=os.environ)
        else:
            print("You should probably add some parameters first.")