API Reference
=============

The Python control layer under ``src/``. It contains no physics — only the
configuration schema, the loading and macro-writing step, and the subprocess
runner. The GEANT4 engine is driven entirely through the macro these produce.

Configuration schema (``models``)
----------------------------------

The Pydantic models that describe one experiment and double as the run record.

.. automodule:: models.base
   :members:

.. automodule:: models.simulation
   :members:

.. automodule:: models.source
   :members:

.. automodule:: models.sample
   :members:

.. automodule:: models.shielding
   :members:

.. automodule:: models.detector
   :members:

.. automodule:: models.run
   :members:

.. automodule:: models.runner
   :members:

.. automodule:: models.environment
   :members:

.. automodule:: models.metadata
   :members:

.. automodule:: models.vectors
   :members:

Configuration loading and macro writing (``config``)
-----------------------------------------------------

Read a YAML configuration, validate it as a ``Simulation``, and turn it into the
GEANT4 macro the engine reads.

.. automodule:: config.yaml_io
   :members:

.. automodule:: config.macro
   :members:

Runner (``runner``)
-------------------

Prepare the run folder, launch ``graace-sim``, stream its output, and verify the
results.

.. automodule:: runner.run_simulation
   :members:
