from setuptools import setup, find_packages

setup(
    name="devstandards-mcp",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "mcp>=0.1.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.9.0",
        "aiosqlite>=0.19.0",
        "pandas>=2.0.0",
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "devstandards-server=src.server:main",
        ],
    },
)