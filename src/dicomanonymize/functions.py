from os import listdir
from pydicom import dcmread
import pandas as pd
import datetime
from multiprocessing.pool import ThreadPool
from functools import partial
import numpy as np
import random
from numba import jit, int32, void

from .classes import Patient, VALUES_TO_ANONYMIZE

from pathlib import Path


def anonymize(
    input_directory: Path,
    output_directory: Path = None,
    patients: list = None,
    parallel: bool = True,
):
    """
    Anonymize patients data

    :param input_directory: Path of the input directory
    :param output_directory: Path of the output directory
    :param patients: list of Patient objects
    :param parallel: use CPU multithreading
    :return: None
    """

    if output_directory is None:
        output_directory = input_directory
    output_directory.mkdir(parents=True, exist_ok=True)

    if patients is None:
        patients = read_patients(input_directory)
    anonymize_id_patients(patients)
    anonymize_patients(output_directory, patients, parallel)
    write_conversion_table(output_directory, patients)


def get_directories(path: Path):
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


def get_patients(lookup_directories: list):
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
                    # print(f"{val} not found")
                    temp_dict[val] = None
            patients.append(
                Patient(
                    temp_dict,
                    [d],
                    [d],
                )
            )

    return patients


@jit(void(int32[:], int32), nopython=True)
def shuffle(array, num_times):
    """
    Shuffle the array

    :param array: np.array of int32 to be shuffled
    :param num_times: int number of times to shuffle the array
    :return: None
    """

    for _ in range(num_times):
        x = random.randint(0, len(array) - 1)
        y = random.randint(0, len(array) - 1)
        temp = array[x]
        array[x] = array[y]
        array[y] = temp


def generate_ids(seed: int, length: int):
    """
    Randomly generate ids

    :param seed: int
    :param length: int length of the generated array
    :return: list of ids
    """

    ids = np.arange(length, dtype=np.int32)

    # this ensures constant behavior
    # comment the line if you want "more random" numbers
    random.seed(seed)

    shuffle(ids, length * 100)

    return ids


def anonymize_id_patients(patients: list):
    """
    Generate an anonymized id for each patient

    :param patients: list of Patient objects
    :return: None
    """

    seed = 0
    length = max(len(patients), 1000)
    ids = generate_ids(seed, length)

    for i, p in enumerate(patients):
        p.generate_anonymized_id(ids[i])


def anonymize_patient(output_dir: Path, parallel: bool, patient: Patient):
    """
    Generate an anonymized id for each patient

    :param output_dir: Path of the output directory
    :param parallel: use CPU multithreading
    :param patient: Patient to be anonymized
    :return: None
    """

    patient.anonymize(output_dir, parallel)


def anonymize_patients(output_dir: Path, patients: list, parallel: bool):
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


def read_patients(input_dir: Path):
    """
    Read patients information

    :param input_dir: Path of the input directory
    :return: list of patients
    """

    lookup_directories = get_directories(input_dir)

    patients = get_patients(lookup_directories)

    return patients


def write_conversion_table(output_directory: Path, patients: list):
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
