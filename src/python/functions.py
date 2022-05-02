from pathlib import Path
from os import listdir
from pydicom import dcmread

from classes import Patient


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
            if p.patient_id == ds.PatientID:
                already_defined = True
                p.directories.append(d)
                break
        if not already_defined:
            patients.append(
                Patient(
                    ds.PatientName.given_name.title(),
                    ds.PatientName.family_name.title(),
                    ds.PatientID,
                    "0",
                    [d],
                )
            )

    return patients


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

    # for testing only
    input_dir = Path("C:\\") / "Users" / "palazzo.gabriele" / "Downloads" / "TestMimDicom"

    lookup_directories = get_directories(input_dir)

    patients = get_patients(lookup_directories)

    for p in patients:
        print(p)

    return 0
