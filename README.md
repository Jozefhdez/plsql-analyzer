# PL/SQL Static Analyzer

A python script that performs static analysis on PL/SQL code.

## Features

- Detects undeclared variables.
- Detects unused variables.
- Checks for unbalanced BEGIN/END blocks.
- Flags unreachable code after RETURN.
- Generates a basic metric report.

## Files

```
analyzer.py # Main script
sample.sql  # Example PL/SQL code
report.txt  # Output with results
```

## How to run

1. Place your PL/SQL code in `sample.sql`
2. Run the analyzer:
   ```
   python3 analyzer.py
   ```
3. Results will be saved to `report.txt`
