from setuptools import setup, find_packages

setup(
    name="ness_automation",
    version="0.1.0",
    description="Automation project for Ness systems",
    author="Ness Automation Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ]
    },
)
