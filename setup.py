import io

from setuptools import setup, find_packages

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

tests_require = [
    "pylint",
    "pytest",
    "pytest-cov",
    "pytest-mock",
    "pytest-click",
]

setup(
    author="Terminal Labs",
    author_email="solutions@terminallabs.com",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.8",
    ],
    description="A cloud, virtual machine, and container provisioning tool",
    entry_points="""
        [console_scripts]
        nursery=nursery.cli:main
    """,
    extras_require={"test": tests_require},
    include_package_data=True,
    install_requires=["click"],
    license="BSD",
    long_description=readme,
    long_description_content_type="text/markdown",
    name="Nursery",
    packages=find_packages(),
    platforms="any",
    tests_require=tests_require,
    url="https://github.com/terminal-labs/nursery",
    version="0.0.1",
)
