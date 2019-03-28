from setuptools import setup, find_packages
setup(
    name='open-answerx',
    version='1.1.7',
    description='{OPEN} client for AnswerX Cloud and Managed',
    author='Diego Xirinachs',
    author_email='dxirinac@akamai.com',
    scripts=['open-answerx.py'],
    url='https://github.com/dxiri/OAT',
    namespace_packages=['akamai'],
    packages=find_packages(),
    python_requires=">=2.7.10",
    install_requires = [
        'edgegrid-python'
    ],
    license='LICENSE.txt'

)
