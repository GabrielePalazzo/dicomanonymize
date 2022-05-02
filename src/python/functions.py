from pathlib import Path
from os import listdir
from pydicom import dcmread

from classes import Patient, VALUES_TO_ANONYMIZE


def get_io_dirs(args):
    """
    Get input and output directories

    :param args: command line arguments
    :return: Path for input directory, Path for output directory
    """
    if args.input_directory is not None:
        input_dir = args.input_directory
    else:
        # if no input directory is specified, default to current working directory
        print(f"Using {Path.cwd()} as input directory")
        input_dir = Path.cwd()
        # for testing only
        input_dir = Path("C:\\") / "Users" / "palazzo.gabriele" / "Downloads" / "TestMimDicom"
        # input_dir = Path("E:\\") / "TestMimDicom"
    if args.output_directory is not None:
        output_dir = args.output_directory
    else:
        # if no output directory is specified, default to current working directory
        print(f"Using {input_dir} as output directory")
        output_dir = input_dir
    return input_dir, output_dir


def get_directories(path):
    """
    Get a list of subdirectories containing dicom images

    :param path: Path
    :return: list of directories containing dicom images
    """

    studies_or_patients = listdir(path)

    directories_for_anonymization = []

    for study_or_patient in studies_or_patients:
        patient_images = listdir(path / study_or_patient)
        for patient_image in patient_images:
            patient_data = listdir(path / study_or_patient / patient_image)
            for d in patient_data:
                if d.endswith(".dcm"):
                    directories_for_anonymization.append(path / study_or_patient / patient_image)
                    break

    return directories_for_anonymization


def get_patients(lookup_directories):
    """
    Get list of patients to be anonymized

    :param lookup_directories: list of directories
    :return: list of Patient objects
    """

    patients = []

    for d in lookup_directories:
        files = listdir(d)
        images = []
        for f in files:
            if f.endswith(".dcm"):
                images.append(f)
        ds = dcmread(d / images[0])
        already_defined = False
        for p in patients:
            if p.patient_data["PatientID"] == ds.PatientID:
                already_defined = True
                p.directories.append(d)
                break
        if not already_defined:
            temp_dict = {}
            for val in VALUES_TO_ANONYMIZE:
                temp_dict[val] = ds[val].value
            patients.append(
                Patient(
                    temp_dict,
                    [d],
                )
            )

    return patients


def anonymize_id_patients(patients):
    """
    Generate an anonymized id for each patient

    :param patients: list of Patient objects
    :return: None
    """
    for p in enumerate(patients):
        p[1].generate_anonymized_id(p[0])


def anonymize_patients(args, patients, parallel):
    """
    Generate an anonymized id for each patient

    :param patients: list of Patient objects
    :return: None
    """

    _, output_dir = get_io_dirs(args)

    for p in patients:
        p.anonymize(output_dir, parallel)


def read_patients(args):
    """
    Read patients information

    :param args: command line arguments
    :return: list of patients
    """

    input_dir, _ = get_io_dirs(args)

    lookup_directories = get_directories(input_dir)

    patients = get_patients(lookup_directories)

    return patients
