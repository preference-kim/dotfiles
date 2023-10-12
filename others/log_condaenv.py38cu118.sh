#!/bin/bash 

conda create -n py38cu118 pip python=3.8
conda activate py38cu118

conda install -c "nvidia/label/cuda-11.8.0" cuda
nvcc --version # make sure the installation

conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia # pytorch with conda

python # test
    import torch
    x= torch.rand(5,3)
    print(x)
    torch.cuda.is_available()
    exit()