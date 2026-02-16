#!/usr/local/bin/python3
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


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
    src = Path(os.environ['nnUNet_preprocessed']) / dataset_name
    dst = prepdir / dataset_name
    print(f'Copying processed data for dataset {dataset_name} to compute node')
    if not os.path.exists(dst):
        prepdir.mkdir(parents=True, exist_ok=True)
        transfers = int(os.environ.get('NNUNET_COPY_TRANSFERS', '16'))
        streams = int(os.environ.get('NNUNET_COPY_STREAMS', '16'))
        rclone_cmd = [
            'rclone', 'copy', str(src) + '/', str(dst),
            '--progress', '--transfers', str(transfers),
            '--multi-thread-streams', str(streams),
            '--no-update-modtime',
        ]
        try:
            rclone_result = subprocess.run(rclone_cmd)
            if rclone_result.returncode != 0:
                print('rclone failed, falling back to built-in copy')
                shutil_sol.copytree(src, dst)
        except FileNotFoundError:
            print('rclone not found, falling back to built-in copy')
            shutil_sol.copytree(src, dst)

    os.environ['nnUNet_preprocessed'] = str(prepdir)
    print("Running:", argv)
    result = subprocess.run(argv, env=os.environ)
    if result.returncode == 0:
        shutil.rmtree(prepdir / dataset_name, ignore_errors=True)
    sys.exit(result.returncode)


if __name__ == '__main__':
    os.environ['nnUNet_raw'] = '/nnunet_data/nnUNet_raw'
    os.environ['nnUNet_preprocessed'] = '/nnunet_data/nnUNet_preprocessed'
    os.environ['nnUNet_results'] = '/nnunet_data/nnUNet_results'

    actions = {'nnUNetv2_train': wrap_train}

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