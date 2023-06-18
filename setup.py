from setuptools import setup, find_packages


setup(
    name=find_packages()[0],
    version="0.0.1",  # We are not using python module versioning. All handled through docker.
    packages=find_packages(),
    python_requires=">=3.8",
    include_package_data=True,  # Note - we install via pip -e, so we don't need to worry about package data.
    install_requires=[
        "click==8.1.3",
        "requests==2.30.0",
    ],
    entry_points={
        'console_scripts': [
            'pytw5 = pytw5.cli:root_cmd'
        ]
    }
)
