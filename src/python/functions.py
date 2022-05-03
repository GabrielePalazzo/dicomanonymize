from os import listdir
from pydicom import dcmread
import pandas as pd
import datetime
from multiprocessing.pool import ThreadPool
from functools import partial

from classes import Patient, VALUES_TO_ANONYMIZE


def get_directories(path):
    """
    Get a list of subdirectories containing dicom images

    :param path: Path
    :return: list of directories containing dicom images
    """

    studies_or_patients = listdir(path)

    directories_for_anonymization = []

    for study_or_patient in studies_or_patients:
        try:
            patient_images = listdir(path / study_or_patient)
            for patient_image in patient_images:
                patient_data = listdir(path / study_or_patient / patient_image)
                for d in patient_data:
                    if d.endswith(".dcm"):
                        directories_for_anonymization.append(
                            path / study_or_patient / patient_image
                        )
                        break
        except Exception:
            print("Not a directory")

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
                p.source_directories.append(d)
                p.destination_directories.append(d)
                break
        if not already_defined:
            temp_dict = {}
            for val in VALUES_TO_ANONYMIZE:
                try:
                    temp_dict[val] = ds[val].value
                except Exception:
                    print(f"{val} not a found")
                    temp_dict[val] = None
            patients.append(
                Patient(
                    temp_dict,
                    [d],
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


def anonymize_patient(output_dir, parallel, patient):
    """
    Generate an anonymized id for each patient

    :param output_dir: Path of the output directory
    :param patients: Patient to be anonymized
    :param parallel: use CPU multithreading
    :return: None
    """

    patient.anonymize(output_dir, parallel)


def anonymize_patients(output_dir, patients, parallel):
    """
    Generate an anonymized id for each patient

    :param output_dir: Path of the output directory
    :param patients: list of Patient objects
    :param parallel: use CPU multithreading
    :return: None
    """

    if parallel:
        num_threads = max(len(patients), 1)
        with ThreadPool(num_threads) as p:
            p.map(partial(anonymize_patient, output_dir, parallel), patients)
    else:
        for p in patients:
            anonymize_patient(output_dir, parallel, p)


def read_patients(input_dir):
    """
    Read patients information

    :param input_dir: Path of the input directory
    :return: list of patients
    """

    lookup_directories = get_directories(input_dir)

    patients = get_patients(lookup_directories)

    return patients


def write_conversion_table(output_directory, patients):
    """
    Write all patient information to a csv file, in order to be able to de-anonymize data

    :param output_directory: Path of the output directory
    :param patients: list of Patient objects
    :return: None
    """

    df = pd.DataFrame()

    position = 0
    df.insert(position, "anonymized_id", "")
    for i, p in enumerate(patients):
        df.at[i, "anonymized_id"] = p.anonymized_id
    position += 1

    # df.insert(position, "destination_directories", "")
    # for i, p in enumerate(patients):
    #    df.at[i, "destination_directories"] = p.destination_directories
    # position += 1

    for val in VALUES_TO_ANONYMIZE:
        df.insert(position, val, "")
        for i, p in enumerate(patients):
            df.at[i, val] = str(p.patient_data[val])
        position += 1

    csv_name = "Anonymization.csv"

    files_list = listdir(output_directory)

    if csv_name in files_list:
        csv_name = f'Anonymization-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.csv'
        if csv_name in listdir(output_directory):
            print(
                "Cannot find a unique name for the conversion table. Aborting write_conversion_table..."
            )
            return

    df.to_csv(output_directory / csv_name, index=False)
