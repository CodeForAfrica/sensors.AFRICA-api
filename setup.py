import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setuptools.setup(
    name="sensors_africa",
    version="0.0.1",
    author="CodeForAfrica",
    description="Api to save and access data from deployed sensors.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CodeForAfricaLabs/sensors.AFRICA-api",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)