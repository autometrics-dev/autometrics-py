from setuptools import setup, find_packages

setup(
    name='autometrics',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'prometheus_client',
        'prometheus_api_client',
        'python-dotenv'
    ]
)