from setuptools import setup, find_packages

setup(
    name="youth_housing_monitor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "apache-airflow==2.10.5",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "python-dotenv==1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest==8.0.0",
            "pytest-cov==4.1.0",
        ],
    },
) 