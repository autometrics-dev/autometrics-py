from setuptools import setup, find_packages

setup(
    name="autometrics",
    version="0.3",
    packages=find_packages(),
    install_requires=["prometheus_client", "python-dotenv"],
)
