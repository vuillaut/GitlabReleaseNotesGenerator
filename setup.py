"""Python setup.py for gitlab_release_notes package"""
import io
import os
from setuptools import find_packages, setup
import re

def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("gitlab_release_notes", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """
    content = ""
    with io.open(
            os.path.join(os.path.dirname(__file__), *paths),
            encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def get_version():
    with open(os.path.join(os.path.dirname(__file__), 'gitlab_release_notes/version.py')) as f:
        result = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format('__version__'), f.read())
    return result.group(1)


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="gitlab_release_notes",
    version=get_version(),
    description="Generate release notes for a gitlab project",
    url="https://github.com/vuillaut/gitlab_release_notes",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="vuillaut",
    packages=find_packages(exclude=["gitlab_release_notes/tests", ".github"]),
    install_requires=['python-gitlab>=3.0', 'python-dateutil'],
    entry_points={
        "console_scripts": ["gitlab-release-notes = gitlab_release_notes.generate:main"]
    },
    extras_require={"test": ['pytest']},
)
