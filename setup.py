from setuptools import setup, find_packages
setup(
    name='open-answerx',
    version='2.0.2',
    description='{OPEN} client for AnswerX Cloud and Managed',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    author='Diego Xirinachs',
    author_email='dxirinac@akamai.com',
    scripts=['open-answerx.py'],
    url='https://github.com/dxiri/OAT',
    namespace_packages=['akamai'],
    packages=find_packages(),
    python_requires=">=3.4",
    install_requires = [
        'edgegrid-python',
        'requests'
    ],
    license='LICENSE.txt'

)
