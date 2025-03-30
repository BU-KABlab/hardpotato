from setuptools import find_packages, setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="hardpotato",
    version="1.3.14",
    description="Python API to control programmable potentiostats.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Oliver Rodriguez, Odin Holmes, Gregory Robben",
    author_email="oliver.rdz@softpotato.xyz",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/BU-KABlab/hardpotato",
    keywords="Electrochemistry",
    install_requires=["numpy", "scipy", "matplotlib", "softpotato", "pyserial"],
)
