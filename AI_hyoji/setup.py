import os
from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CppExtension
from os.path import join

project_root = "Correlation_Module"

# CUDA 없이 필요한 소스 파일만 남김
source_files = ["correlation.cpp", "correlation_sampler.cpp"]

# MSVC (Windows용 Visual Studio 컴파일러)에서는 '-std=c++17', '-fopenmp' 같은 GCC 옵션을 무시하므로 제거
# cxx_args = ["-std=c++17", "-fopenmp"]
cxx_args = ["/std:c++17"]  # Windows 환경에서는 이걸로 충분

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

sources = [join(project_root, file) for file in source_files]

setup(
    name="spatial_correlation_sampler",
    version="0.5.0-cpu",
    author="Clément Pinard",
    author_email="mail@clementpinard.fr",
    description="Correlation module for PyTorch (CPU-only)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ClementPinard/Pytorch-Correlation-extension",
    install_requires=["torch>=1.1", "numpy"],
    ext_modules=[
        CppExtension(
            "spatial_correlation_sampler_backend",
            sources,
            define_macros=[],  # CUDA 없음
            extra_compile_args={"cxx": cxx_args},
        )
    ],
    package_dir={"": project_root},
    packages=["spatial_correlation_sampler"],
    cmdclass={"build_ext": BuildExtension},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
