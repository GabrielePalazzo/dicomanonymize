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
    arg_parser.add_argument(
        "-s",
        "--single_thread",
        help="Run on single thread (slower but more robust)",
        action="store_true",
    )

    args = arg_parser.parse_args(args)

    return args


def anonymize():
    """
    Anonymize patients data

    :return: None
    """

    args = parse_args()
    parallel = not args.single_thread
    patients = func.read_patients(args)
    func.anonymize_id_patients(patients)
    func.anonymize_patients(args, patients, parallel)


if __name__ == "__main__":
    anonymize_patients_start = time.time()
    anonymize()
    anonymize_patients_final = time.time()
    print(f"> Anonymize_Patients took: {anonymize_patients_final - anonymize_patients_start:.4}s")
