"""
"""

import numpy as np

NO_CHORD = "N"

def load_labfile(lab_file):
    """Load a lab file into a time array and a list of corresponding labels.

    Parameters
    ----------
    lab_file : string
        Path to an HTK chord label file.

    Returns
    -------
    boundaries : np.ndarray
        Chord boundaries, in seconds. Monotonically increasing.
    labels : list
        Chords labels corresponding to the time between boundaries.

    Note that len(time_points) = len(labels) + 1.
    """
    boundaries = []
    labels = []
    for i, line in enumerate(open(lab_file)):
        line = line.strip("\n")
        if not line:
            # Assume we're done?
            break
        line_parts = line.split("\t")
        if len(line_parts) != 3:
            raise ValueError(
                "Error parsing %s on line %d: %s" % (lab_file, i, line))
        start_time, end_time = float(line_parts[0]), float(line_parts[1])
        boundaries.append(start_time)
        labels.append(line_parts[-1])
    boundaries = np.array(boundaries + [end_time])
    assert np.diff(boundaries).min() > 0, \
        "Boundaries are not monotonically increasing."
    return boundaries, labels


def assign_labels_to_time_points(time_points, boundaries, labels):
    """Assign chord labels to a set of points in time.

    Parameters
    ----------
    time_points : array_like

    boundaries : np.ndarray

    labels : array_like

    Returns
    -------
    output_labels : list
        Chord labels corresponding to the input time points.
    """
    output_labels = []
    for t in time_points:
        if t < boundaries.min() or t > boundaries.max():
            output_labels.append(NO_CHORD)
        index = np.argmax(boundaries > t) - 1
        output_labels.append(labels[index])
    return output_labels
