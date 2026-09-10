# Output (IO)

The engine writes detector responses as Parquet files. The Python runner sets the
base path to:

```text
<run_directory>/results/gamma_hits.parquet
```

`SimIO` changes that base into one directory per detector and one or more part
files per worker:

```text
results/
├── geometry.png
└── <detector_name>/
    ├── gamma_hits-part-w000-00000.parquet
    └── gamma_hits-part-w001-00000.parquet
```

The exact number of files depends on the number of workers and the number of
responses. A buffer is flushed after one million hits for a detector, so a long
run can create multiple part files per worker.

## Columns

Each Parquet part contains two `float64` columns:

| Column | Unit | Meaning |
| --- | --- | --- |
| `energy` | keV | Total energy deposited in the detector during one event |
| `time` | ns | Earliest energy-deposit time in that event |

A row is written only when the detector receives positive energy during the
event. The detector name is represented by the parent directory, not a column.
There is no counts column; count spectra can be computed by binning the `energy`
values.

## Threading and ordering

The multithreaded engine gives each worker a thread-local writer. Worker tags in
part filenames prevent collisions, and the set of rows is complete. Row order
across workers is not defined. The Python runner removes the existing `results/`
directory before a rerun so stale part files are not mixed with new output.

## Reading results

PyArrow can read all parts for a detector as one dataset:

```python
from pathlib import Path
import pyarrow.dataset as ds

results = Path("data/example_000/results/hpge")
hits = ds.dataset(results, format="parquet").to_table()
energy_kev = hits.column("energy")
time_ns = hits.column("time")
```

Pandas can be used after converting the table with `hits.to_pandas()`.

## Geometry image and log

The automatic geometry image is written beside the Parquet output as
`results/geometry.png` when `TSG_OFFSCREEN` is available. The engine log is
written by the Python runner to `logs/run.log`. The validated YAML is not copied
into the output; keep it with the run and use the generated `.mac` file as the
exact engine input record.
