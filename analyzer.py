import time


TYPES = ['NUMBER', 'VARCHAR2', 'INT', 'BOOLEAN']


def read_file(filename):
    with open(filename, 'r') as f:
        return f.readlines()


def find_declarations_and_usage(lines):
    declared = set()
    used = set()
    warnings = []
    errors = []
    in_block = 0
    after_return = False

    for i, line in enumerate(lines, start=1):
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith('--'):
            continue

        tokens = stripped_line.replace(';', ' ;').split()  # handle ; as token
        tokens_upper = [t.upper() for t in tokens]

        for j, token in enumerate(tokens_upper):
            if token in TYPES and j > 0:
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

    return declared, used, in_block, warnings, errors


def analyze_variables(declared, used):
    warnings = []
    unused = declared - used
    undeclared = used - declared

    for var in unused:
        warnings.append(f'Variable {var} is declared but never used.')
    for var in undeclared:
        warnings.append(f'Variable {var} used before declaration.')

    return warnings


def generate_report(errors, warnings, metrics, filename='report.txt'):
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


def main(filename):
    start = time.time()
    lines = read_file(filename)

    declared, used, in_block, warnings, errors = find_declarations_and_usage(
        lines)
    warnings += analyze_variables(declared, used)

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

    generate_report(errors, warnings, metrics)


if __name__ == '__main__':
    main('sample.sql')
