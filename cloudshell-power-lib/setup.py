import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cloudshell-power-lib",
    version="1.0.0",
    author="Quali Customer Success",
    author_email="tim.s@quali.com",
    description="Quali Power Management support library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/QualiSystemsLab/Power-Management",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2 :: Only",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=['cloudshell-shell-core>=2.3.0,<2.4.0',
                      'cloudshell-orch-core>=2.0.0.0,<2.1.0.0',
                      'cloudshell-automation-api>=9.0.0.0,<9.1.0.0'],
)