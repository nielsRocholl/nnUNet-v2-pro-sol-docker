## Extending nnUNetv2

These folders are copied into the nnunetv2 library when building the docker image, allowing for extensions to the nnunetv2 codebase. 

**Do not** overwrite/modify/extend any original files/classes/functions to prevent breaking the library. **Do** follow the nnunetv2 folder structure when adding files here so they get added correctly. 

Try to use descriptive filenames for your extensions e.g. for the ULS23 project I wanted to run experiments with different trainers (to use different learning rates when pre-training models). These are found under */nnunetv2/training/nnUNetTrainer/[customTrainersULS.py](nnunetv2%2Ftraining%2FnnUNetTrainer%2FcustomTrainersULS.py)*. 
Document your extensions below so other users don't need to implement the same modifications.

### Extensions:

#### No resampling:
In order to train without resampling your data you can use the 'no_resampling_data_or_seg_to_shape' function in your plans file to be used with 'resampling_fn_data', 'resampling_fn_seg' and 'resampling_fn_probabilities'. Implemented here: 
[custom_resampling.py](nnunetv2%2Fpreprocessing%2Fresampling%2Fcustom_resampling.py)