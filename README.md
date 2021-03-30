# RayBender - Fast Python Ray-Tracing

RayBender is a Python package for fast CPU rendering using the Intel® Embree backend.

## Installation

1. Clone the repository and its submodules by running:

```sh
git clone --recursive git@github.com:cvg/raybender.git
cd raybender
```

2. Install Embree following the [official instructions](https://www.embree.org/downloads.html) and set the environmental variable `embree_DIR` to point to `embree-config.cmake`. On Linux, this can be done as follows:

```sh
wget https://github.com/embree/embree/releases/download/v3.12.2/embree-3.12.2.x86_64.linux.tar.gz
tar xvzf embree-3.12.2.x86_64.linux.tar.gz
rm embree-3.12.2.x86_64.linux.tar.gz
mv embree-3.12.2.x86_64.linux embree-3.12.2
export embree_DIR=`readlink -f embree-3.12.2/lib/cmake/embree-3.12.2`
```

3. Finally, RayBender can be installed using pip:

```sh
pip install .
```

## Examples

Start by setting up the demo conda environment by running `conda env create -f examples/env.yml` and activate it `conda activate raybender`. Next, install RayBender by following the instructions above. Please refer to `examples/demo.py` for a minimal RGBD rendering examples from a triangle mesh.
