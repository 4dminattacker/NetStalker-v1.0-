from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="netstalker",
    version="2.0.0",
    author="4dmin attacker",
    author_email="4dminattacker@gmail.com",
    description="Professional WiFi penetration testing suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/4dminattacker/NetStalker-v1.0-",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "customtkinter>=5.0.0",
        "Pillow>=9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "netstalker-cli=netstalker.cli:main",
            "netstalker-gui=netstalker.gui:main",
        ],
    },
)
