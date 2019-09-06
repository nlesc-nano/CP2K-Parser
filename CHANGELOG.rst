###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

1.0.1
*****

Changed
-------
* Trailing whitespaces are now removed from keys.
* Content of the `&COORD`_ block is now converted into a
  dictionary with ``"_1"`` as key and a list of atomic symbols + coordinates
  as values.

.. _`&COORD`: https://manual.cp2k.org/cp2k-6_1-branch/CP2K_INPUT/FORCE_EVAL/SUBSYS/COORD.html


1.0.0
*****

Added
-----
* Release of CP2K-Parser
