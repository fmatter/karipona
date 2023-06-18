import setuptools

setuptools.setup(
    name="karipona",
    version="0.0.1",
    author="Florian Matter",
    author_email="florianmatter@gmail.com",
    description="Cariban languages data for CLDF projects",
    url="https://github.com/fmatter/karipona",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "attrs",
        "certifi",
        "charset-normalizer",
        "clldutils",
        "colorlog",
        "csvw",
        "download",
        "idna",
        "isodate",
        "latexcodec",
        "pybtex",
        "pycldf",
        "python-dateutil",
        "PyYAML",
        "regex",
        "requests",
        "rfc3986",
        "segments",
        "six",
        "tabulate",
        "tqdm",
        "uritemplate",
        "urllib3",
    ],
    entry_points={
        "console_scripts": ["cmeta_download=karipona.download:main"],
    },
    python_requires=">=3.6",
)
