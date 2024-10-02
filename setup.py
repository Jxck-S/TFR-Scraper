import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tfr_scraper",
    version="0.1.2",
    author="Jack Sweeney",
    description="FAA TFR Scraper",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/Jxck-S/TFR-Scraper/tree/main",
    project_urls={
        "Bug Tracker": "https://github.com/Jxck-S/TFR-Scraper/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
    'untangle',
    'pandas',
    'html-table-parser-python3'
    ],
)