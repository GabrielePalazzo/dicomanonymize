import argparse
from pathlib import Path
import time

import functions as func


def parse_args(args=None):
    """
    Parse command line arguments
    :param args: already parsed args

    :return: arguments
    """

    arg_parser = argparse.ArgumentParser(__doc__)

    arg_parser.add_argument(
        "-i",
        "--input_directory",
        help="Input path for the original files",
        type=Path,
    )
    arg_parser.add_argument(
        "-o",
        "--output_directory",
        help="Input path for the new files",
        type=Path,
    )

    args = arg_parser.parse_args(args)

    return args


if __name__ == "__main__":
    arguments = parse_args()
    anonymize_patients_start = time.time()
    func.read_patients(arguments)
    anonymize_patients_final = time.time()
    print(f"> Anonymize_Patients took: {anonymize_patients_final - anonymize_patients_start:.4}s")
