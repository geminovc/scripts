# nets_scripts

## Requirements
```bash
pip install pandas scapy
```

```bash
sudo apt install r-base r-base-core r-recommended mahimahi net-tools
```

Install the following R packages (by running R and executing `install.packages("[package_name]"`)
```bash
ggplot2 cowplot sysfonts showtext showtextdb
```

## Conda environment
To install the conda environment from the `.txt` file use:

```bash
conda create --name your-env-name --file pantea-fom.txt
```

If you get `ArchiveErrors` while installing the environment, run `conda config --show` to see your configs. Then run:
```bash
conda config --add pkgs_dirs /dir-you-have-write-access-to
conda config --prepend envs_dirs /dir-you-have-write-access-to/envs
conda config --prepend pkgs_dirs /dir-you-have-write-access-to/pkgs
conda config --set root_prefix /dir-you-have-write-access-to
```

You might need to install the followings in your environment if there are issues in the `.txt` file:
```bash
conda activate your-env-name

pip install opencv-python
pip install --upgrade google-api-python-client
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113
conda install tensorboardX
pip install piq
conda install -c conda-forge scipy 
conda install -c conda-forge scikit-image
pip install imageio-ffmpeg
pip install flow_vis
pip install bitstring
```

## Profiling

If you need to profile the codes and experiment, you can use the notes in [here](https://docs.google.com/document/d/1eoKbvsJqGzWpVhIgzSxBhVUblqyBeDmsyUrHWP6sKrA/edit?usp=sharing)
