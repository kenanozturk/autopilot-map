from setuptools import find_packages, setup

if __name__ == '__main__':
    with open("README.md", "r", encoding='utf8') as fh:
        long_description = fh.read()

    setup(
        name='autopilot-map',
        packages=find_packages(),
        version='0.1.0',
        description='A short description of the project.',
        author='Your name (or your organization/company/team)',
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="bitbucket.tomtomgroup.com:7999/taigr/taigr_autopilot-map.git",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ],
    )
