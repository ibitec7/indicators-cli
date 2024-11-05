from setuptools import setup, find_packages

setup(
    name="indicators-cli",                   
    version="0.1.2",
    author="Syed Ibrahim Omer",
    author_email="syed.ibrahim.omer.2@gmail.com",
    description="CLI tool to calculate stock indicators",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ibitec7/indicators-cli",
    packages=find_packages(),                
    install_requires=[
        "pandas",
        "numpy",
        "yfinance",
        "click"                               
    ],
    entry_points={
        'console_scripts': [
            'indicators=indicators.cli:main',            
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
