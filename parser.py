def parse(file, delimiter):
    file_contents_by_row = []
    last_line = None
    first_line = True
    with open(file) as sample_file:
        for line in sample_file:
            if first_line:
                first_line = False
            elif not last_line:
                row = line.split(delimiter)
                file_contents_by_row.append(row)
    return file_contents_by_row