import time


def analyze_file(filename):
    start = time.time()
    with open(filename, 'r') as f:
        lines = f.readlines()

    declared = set()
    used = set()
    warnings = []
    errors = []
    in_block = 0
    after_return = False

    types = ['NUMBER', 'VARCHAR2', 'INT', 'BOOLEAN']

    for i, line in enumerate(lines, start=1):
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith('--'):
            continue

        tokens = stripped_line.replace(';', ' ;').split()  # handle ; as token
        tokens_upper = [t.upper() for t in tokens]

        for j, token in enumerate(tokens_upper):
            if token in types and j > 0:
                var_name = tokens[j - 1].strip(';')
                declared.add(var_name.lower())  # add all declared variables

        # check usage by adding used variables
        # (idx - 1, since we want previous token to ':=' or '=')
        if ':=' in tokens_upper:
            idx = tokens_upper.index(':=')
            used.add(tokens[idx - 1].lower())

        if '=' in tokens_upper:
            idx = tokens_upper.index('=')
            used.add(tokens[idx - 1].lower())

        # balance of BEGIN and END
        if stripped_line.upper().startswith('BEGIN'):
            in_block += 1
        if 'END' in tokens_upper:
            in_block -= 1
            if in_block < 0:
                errors.append(f'Line {i}: unmatched END.')

        if 'RETURN' in tokens_upper:
            after_return = True
        elif after_return:
            exec_tokens = [t for t in tokens_upper if t not in (
                ';', 'END', 'BEGIN', 'RETURN', '/', '')]
            if exec_tokens:
                warnings.append(f'Line {i}: code after RETURN statement.')

    unused = declared - used
    undeclared = used - declared

    for var in unused:
        warnings.append(f'Variable {var} is declared but never used.')
    for var in undeclared:
        warnings.append(f'Variable {var} used before declaration.')

    if in_block > 0:
        errors.append(f"Unmatched BEGIN: {in_block} block(s) not closed.")

    elapsed = time.time() - start

    metrics = {
        'Lines': len(lines),
        'Declared': len(declared),
        'Used': len(used),
        'Errors': len(errors),
        'Warnings': len(warnings),
        'Time': round(elapsed, 4)
    }

    with open('report.txt', 'w') as out:
        out.write('Report\n\n')
        for e in errors:
            out.write('ERROR: ' + e + '\n')
        for w in warnings:
            out.write('WARNING: ' + w + '\n')
        out.write('\nMETRICS\n\n')
        for key, value in metrics.items():
            out.write(f'{key}: {value}\n')

    print('Report saved to report.txt')


if __name__ == '__main__':
    analyze_file('sample.sql')
