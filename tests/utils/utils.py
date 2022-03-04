from typing import List, Dict

def build_cursor_results_as_dict(cursor) -> List[Dict[str, str]]:
    """ Makes a dictionary out of the cursor's result.
    :param cursor: The cursor. """

    columns = [column[0] for column in cursor.description]

    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))

    return results