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


def anonymize(input_directory, output_directory, parallel=True):
    """
    Anonymize patients data

    :param input_directory: Path of the input directory
    :param output_directory: Path of the output directory
    :param parallel: use CPU multithreading
    :return: None
    """

    patients = func.read_patients(input_directory)
    func.anonymize_id_patients(patients)
    func.anonymize_patients(output_directory, patients, parallel)


if __name__ == "__main__":
    anonymize_patients_start = time.time()

    arguments = parse_args()
    if arguments.input_directory is not None:
        input_dir = arguments.input_directory
    else:
        # if no input directory is specified, default to current working directory
        print(f"Using {Path.cwd()} as input directory")
        input_dir = Path.cwd()
        # for testing only
        input_dir = Path("C:\\") / "Users" / "palazzo.gabriele" / "Downloads" / "TestMimDicom"
        # input_dir = Path("E:\\") / "TestMimDicom"
    if arguments.output_directory is not None:
        output_dir = arguments.output_directory
    else:
        # if no output directory is specified, default to current working directory
        print(f"Using {input_dir} as output directory")
        output_dir = input_dir

    anonymize(input_dir, output_dir, not arguments.single_thread)
    anonymize_patients_final = time.time()
    print(f"> Anonymize_Patients took: {anonymize_patients_final - anonymize_patients_start:.4}s")
