# Independent report indexer example

This is a new implementation using synthetic DOCX files. It is not company source code or a masked company report. Python standard library only.

```text
python -I make_samples.py
python -I report_indexer.py samples --month 2026-10 --output result
python -I verify.py
```

The example reads paragraph style IDs VulnHeading, Performer and ProjectName and filters by the modified date in docProps/core.xml. Real documents require explicit style mapping and a separately agreed date rule. Repeated metadata within one report is deduplicated. The tool reports missing metadata instead of inferring it. The counts describe document participation, not employee performance. No network requests are made.
