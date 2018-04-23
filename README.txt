OAT - OPEN AnswerX Tool
=======================

This script implements a way to easily interact with the AnswerX OPEN API. You can dump tables, 
view its schema and target either production or staging environments.
The tool works on top of `Akamai {OPEN} Edgegrid Authentication`_ scheme. For more information
visit the `Akamai {OPEN} Developer Community`_.

To learn more about how Edgegrid works, visit:

.. _`requests`: http://docs.python-requests.org
.. _`Akamai {OPEN} Edgegrid authentication`: https://developer.akamai.com/introduction/Client_Auth.html
.. _`Akamai {OPEN} Developer Community`: https://developer.akamai.com

Installation
------------

If you already have edgegrid installed, you can just put this script alongside your .edgerc file and it should just work.

If not, just clone this repo (this repo has an edgegrid implementation bundled in) and then do:

.. code-block:: bash

    $ python setup.py install

To run tests:

.. code-block:: bash

    $ virtualenv -p python2.7 venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt
    $ python -m unittest discover

Contribute
----------

#. Fork `the repository`_ to start making your changes to the **master** branch
#. Write a test which shows that the bug was fixed or that the feature works as expected.
#. Send a pull request and bug the maintainer until it gets merged and published.  :)

.. _`the repository`: https://github.com/akamai-open/AkamaiOPEN-edgegrid-python

Author
------

Diego Xirinachs
