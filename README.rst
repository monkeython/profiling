.. .. image:: https://travis-ci.org/monkeython/profiling.svg?branch=master
..     :target: https://travis-ci.org/monkeython/profiling
..     :alt: Build status
.. 
.. .. image:: https://coveralls.io/repos/monkeython/profiling/badge.png?branch=master
..     :target: https://coveralls.io/r/monkeython/profiling?branch=master
..     :alt: Test coverage
.. 
.. .. image:: https://readthedocs.org/projects/profiling/badge/?version=latest&style=default
..     :target: http://profiling.readthedocs.org/en/latest/
..     :alt: Documentation status
.. 
.. .. image:: https://pypip.in/download/profiling/badge.svg?period=month
..     :target: https://pypi.python.org/pypi/profiling/
..     :alt: Downloads
.. 
.. .. image:: https://pypip.in/version/profiling/badge.svg?text=pypi
..     :target: https://pypi.python.org/pypi/profiling/
..     :alt: Latest Version
.. 
.. .. image:: https://pypip.in/status/profiling/badge.svg
..     :target: https://pypi.python.org/pypi/profiling/
..     :alt: Development Status
.. 
.. .. image:: https://pypip.in/py_versions/profiling/badge.svg
..     :target: https://pypi.python.org/pypi/profiling/
..     :alt: Supported Python versions
.. 
.. .. image:: https://pypip.in/egg/profiling/badge.svg
..     :target: https://pypi.python.org/pypi/profiling/
..     :alt: Egg Status
.. 
.. .. image:: https://pypip.in/wheel/profiling/badge.svg
..     :target: https://pypi.python.org/pypi/profiling/
..     :alt: Wheel Status
.. 
.. .. image:: https://pypip.in/license/profiling/badge.svg
..     :target: https://pypi.python.org/pypi/profiling/
..     :alt: License
.. 
.. .. image:: https://pypip.in/implementation/profiling/badge.svg
..     :target: https://pypi.python.org/pypi/profiling/
..     :alt: Supported Python implementations

The purpose of this package is to provide both reasonable statistical and
deterministic profiling to be used in running (multi-threading) production
environment. Up to now, I'm just trying to prove the concept and this package
is just in the pre-alpha stage.

Deterministic profiling design
==============================

The deterministic profiler is mainly an container of row profiling
informations. Actual profiling is performed by any object implementing the same
``_lsprof.Profiler`` interface. Trough the provided decorators and context manager,
developers can control what code they want to profile: information are stored into the
container at the end of each single profile. Profiling and information storage
must be thread and sub-call/recursion wise.

Statistical profiling design
============================

Statistical profiling is performed using ``sys._current_frames``. Both signal
and thread based statistical profiling are provided for flexibility. Each
profile is collected and serialized as soon as it's produced.

Profiling instrumentation/serialization
=======================================

Both deterministic and statistical profiling can be enabled/disabled trough a
class variable, and initially setup with environment variables. Whenever
instructed so, a collector class can collect profiling information and
serialize for later use. This way, developers can decide when/how to profile.


.. You can read more on `Pythonhosted`_ or `Read the Docs`_. Since this package
.. has en extensive docstring documentation as well as code comments, you can
.. read more browsing the source code or in the python interactive shell.
.. 
.. .. _`Pythonhosted`: http://pythonhosted.org/profiling
.. .. _`Read the Docs`: http://profiling.readthedocs.org
