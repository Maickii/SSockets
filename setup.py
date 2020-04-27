import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SSockets",
    version="0.0.1",
    author="Michael Santana, Lily Byan, Harry LeBlanc",
    author_email="michael_santana@student.uml.edu, liliana_byan@student.uml.edu, harry_leblanc@student.uml.edu",
    description="library for cryptography",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Maickii/SSockets",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
