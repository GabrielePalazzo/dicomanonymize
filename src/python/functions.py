from pathlib import Path


def read_patients(args):
    """
    Read patients information
    :param args: command line arguments

    :return: list of patients
    """

    if args.input_directory is not None:
        input_dir = args.input_directory
    else:
        # if no input directory is specified, default to current working directory
        print(f"Using {Path.cwd()} as input directory")
        input_dir = Path.cwd()
    print(input_dir)
    return 0
