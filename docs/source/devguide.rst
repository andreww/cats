.. _devguide:

Developer's guide
=================

Adding a feature / making a change
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ideally, all significant changes would be discussed in an issue as outlined above before 
time is spent writing code (see asking questions, reporting bugs, and suggesting enhancements),
but however changes are made we would like them to be fed into the CATS code via a pull 
request against the ``main`` branch on github. These pull requests should 
outline the reason for the change,
reference any previous discussion, and note any significant issues that may need 
further consideration. A maintainer with write access to the main 
CATS repository who has not been directly involved in
writing the new code or documentation will need to review the pull request prior to merging. 

We do not have a formal style guide, but code changes and additions should seek to follow the style 
established by the existing CATS codebase. CATS has a fairly comprehensive test suite that runs
automatically against all pull requests and new code should either come with new tests or with an
explanation about why tests for the new code are not included. Please indicate where changes to 
behavior have been made (especially where this means changes to the tests have also been needed).  
CATS includes documentation which should be updated by the pull requests making changes to the
code (although documentation only pull requests are welcome). Some of this documentation is
automatically generated (from doc strings and help text for command line tools) so please make
sure that this internal documentation is up to date.

Testing can also be undertaken in an isolated environment prior to making a pull request and this
can make code development significantly easer. We run tests using ``flake8`` for basic linting,
``pytest`` for the majority of unit and integration tests, and ``mypy`` to check type annotations
and for the static analysis this permits. In a checked out copy of the source, the following installs
the prerequisites and runs all tests::

  python3 -m pip install '.[test]'
  python3 -m pip install flake8
  python3 -m pip install '.[types]'
  flake8 . --count --select=E9,F63,F7,F82 --show-source
  python3 -m mypy cats
  python3 -m pytest

A new build incorporating any updates to the documentation is automatically generated for each PR
and will become available from a link within the pull request. 