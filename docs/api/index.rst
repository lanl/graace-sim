API Reference
=============

The ``graace_sim`` Python package contains the configuration schema, YAML loading,
GEANT4 macro writing, and subprocess runner. It does not contain the physics engine.
The stable public entry points are ``graace_sim.load_simulation`` and
``graace_sim.run_simulation``.

Public interface
----------------

.. automodule:: graace_sim
   :members:

Configuration schema (``models``)
----------------------------------

The Pydantic models describe one experiment and validate its YAML configuration.

.. automodule:: graace_sim.models.base
   :members:

.. automodule:: graace_sim.models.simulation
   :members:

.. automodule:: graace_sim.models.source
   :members:

.. automodule:: graace_sim.models.sample
   :members:

.. automodule:: graace_sim.models.shielding
   :members:

.. automodule:: graace_sim.models.detector
   :members:

.. automodule:: graace_sim.models.run
   :members:

.. automodule:: graace_sim.models.runner
   :members:

.. automodule:: graace_sim.models.environment
   :members:

.. automodule:: graace_sim.models.metadata
   :members:

.. automodule:: graace_sim.models.vectors
   :members:

Configuration loading and macro writing (``config``)
-----------------------------------------------------

.. automodule:: graace_sim.config.yaml_io
   :members:

.. automodule:: graace_sim.config.macro
   :members:

Runner (``runner``)
-------------------

.. automodule:: graace_sim.runner.run_simulation
   :members:
