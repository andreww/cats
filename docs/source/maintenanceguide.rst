.. _maintenanceguide:

Maintainer's guide
==================

Cover who is a maintainer
How we add / remove maintainers
How to review


Developer how-to guide
------------------------

Making a new release
^^^^^^^^^^^^^^^^^^^^

Those of us with commit access to the main CATS repository on GitHub are able to generate a new release and publish this to PyPI. This
should be discussed ahead of time (via a PR changing the version string, see 1 below) and once broad agreement is in place a release can be created as follows:

 1. Merge a pull request onto main that updates the CATS version number ``__version__`` in ``__init__.py`` and adds any release notes / key changes to the documentation. We use a "major.minor.patch" semantic versioning scheme; for bug fixes etc. bump the patch number, for significant new features bump the minor version number, for changes that break previous behavior update the major version number.
 2. Check that all tests have passed after the merge and that the "latest" documentation at read the docs is updated.
 3. Create a release via the GitHub web interface. This involves creating a new tag ("v1.2.3" for version "1.2.3"), giving the release a name (just "1.2.3"), and adding short release notes using markdown as needed. Make sure this is "set as the latest release".
 4. After a short time you should be able to check that the new release exists on PyPI and is documented in the stable docs on read the docs.   
