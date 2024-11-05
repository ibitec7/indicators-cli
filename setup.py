from setuptools import setup, find_packages

setup(
    name="indicators-cli",                     # Name of the package
    version="0.1.0",
    author="Syed Ibrahim Omer",
    author_email="syed.ibrahim.omer.2@gmail.com",
    description="CLI tool to calculate stock indicators",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ibitec7/indicators-cli",  # GitHub URL
    packages=find_packages(),                  # Automatically find packages
    install_requires=[
        "pandas",
        "numpy",
        "yfinance",
        "click"                                # Since you’re using Click for CLI
    ],
    entry_points={
        'console_scripts': [
            'indicators=cli:main',             # Command name -> entry function
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
