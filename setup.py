from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pylopi",
    version="1.0.0",
    author="PicoBaz",
    author_email="picobaz3@gmail.com",
    description="Intelligent Log Monitoring & Analysis System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PicoBaz/PyLoPi",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Flask>=3.0.0",
        "Flask-CORS>=4.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
    ],
    entry_points={
        "console_scripts": [
            "pylopi=app:main",
        ],
    },
)