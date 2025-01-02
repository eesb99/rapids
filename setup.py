"""Setup script for RAPIDS package."""
from setuptools import setup, find_packages

setup(
    name="rapids",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "arxiv==1.4.7",
        "redis==4.6.0",
        "click==8.1.7",
        "pandas==2.0.3",
        "tqdm==4.65.0",
    ],
    entry_points={
        "console_scripts": [
            "rapids=rapids.cli:cli",
        ],
    },
    author="RAPIDS Team",
    author_email="rapids@example.com",
    description="Research Article Processing In Daily Summaries",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/eesb99/rapids",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
)
