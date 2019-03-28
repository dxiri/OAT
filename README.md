OAT - OPEN AnswerX Tool
=======================

This script implements a way to easily interact with the AnswerX OPEN API. You can dump tables, 
view its schema and target either production or staging environments.
The tool works on top of `Akamai {OPEN} Edgegrid Authentication`_ scheme. For more information
visit the `Akamai {OPEN} Developer Community`_.

To learn more about how Edgegrid works, visit:

- `Requests`: http://docs.python-requests.org
- `Akamai {OPEN} Edgegrid authentication`: https://developer.akamai.com/introduction/Client_Auth.html
- `Akamai {OPEN} Developer Community`: https://developer.akamai.com

To learn more about AnswerX, visit:

- `DNS For Network Operators`: https://www.akamai.com/us/en/products/network-operator/dnsi-cacheserve.jsp
- `AnswerX {OPEN} API`: https://developer.akamai.com/api/network_operator/answerx/v1.html

Installation
------------

    $ pip install open-answerx

And make sure you have a .edgerc file in your home folder containing your API credentials (create the file if it doesn't exist).

Contribute
----------

#. Fork `the repository` to start making your changes to the **master** branch
#. Write a test which shows that the bug was fixed or that the feature works as expected.
#. Send a pull request and bug the maintainer until it gets merged and published.  :)

`the repository`: https://github.com/dxiri/OAT

Author
------

Diego Xirinachs
