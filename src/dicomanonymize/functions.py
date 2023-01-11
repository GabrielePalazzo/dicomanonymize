"""Anonymization and path acquisition functions."""

from typing import List
from os import listdir
from pydicom import dcmread
import pandas as pd
import datetime
from multiprocessing.pool import Pool, ThreadPool
from multiprocessing import cpu_count
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
    destination_directories: bool = False,
) -> None:
    """
    Anonymize patients data.

    :param input_directory: Path of the input directory (Path)
    :param output_directory: Path of the output directory (Path)
    :param patients: list of Patient objects (list[Patient])
    :param parallel: use CPU multithreading (bool)
    :param destination_directories: anonymize only destination directories (bool)
    :return: None
    """
    if output_directory is None:
        output_directory = input_directory
    output_directory.mkdir(parents=True, exist_ok=True)

    if patients is None:
        patients = read_patients(input_directory)
    anonymize_id_patients(patients)
    anonymize_patients(output_directory, patients, parallel, destination_directories)
    write_conversion_table(output_directory, patients)


def look_into_study_directories(
    study_directory_path: Path, patient_images: List[str]
) -> List[Path]:
    """
    Look for dicom images inside "Studies_xx" folder.

    :param study_directory_path: path to "Studies_xx" directory
    :param patient_images: list of folders containing dicom images
    :return: list of directories containing dicom images inside selected study folder
    """
    directories_for_anonymization = []
    for patient_image in patient_images:
        patient_data: List[str] = listdir(study_directory_path / patient_image)
        for d in patient_data:
            if d.endswith(".dcm"):
                directories_for_anonymization.append(study_directory_path / patient_image)
                break
    return directories_for_anonymization


def get_directories(path: Path) -> List[Path]:
    """
    Get a list of subdirectories containing dicom images.

    :param path: Path
    :return: list of directories containing dicom images
    """
    studies_or_patients = list(path.iterdir())

    directories_for_anonymization = []

    for study_or_patient in studies_or_patients:
        try:
            patient_images = [image_path.name for image_path in study_or_patient.iterdir()]
            if patient_images[0].endswith(".dcm"):
                directories_for_anonymization.append(study_or_patient)
            else:
                directories_for_anonymization.extend(
                    look_into_study_directories(study_or_patient, patient_images)
                )
        except Exception:
            print("Not a directory")

    return directories_for_anonymization


def get_patients(lookup_directories: List[Path]) -> List[Patient]:
    """
    Get list of patients to be anonymized.

    :param lookup_directories: list of directories
    :return: list of Patient objects
    """
    patients = []
    for image_directory in lookup_directories:
        files = [image_file.name for image_file in image_directory.iterdir()]
        images = []
        for dicom_file in files:
            # Keep only dicom files
            if dicom_file.endswith(".dcm"):
                images.append(dicom_file)
        dicom_image = dcmread(image_directory / images[0])
        already_defined = False
        for patient in patients:
            if patient.patient_data["PatientID"] == dicom_image.PatientID:
                already_defined = True
                patient.source_directories.append(image_directory)
                patient.destination_directories.append(image_directory)
                break
        if not already_defined:
            temp_dict = {}
            for value_to_anonymize in VALUES_TO_ANONYMIZE:
                try:
                    temp_dict[value_to_anonymize] = dicom_image[value_to_anonymize].value
                except Exception:
                    # print(f"{value_to_anonymize} not found")
                    temp_dict[value_to_anonymize] = None
            patients.append(
                Patient(
                    temp_dict,
                    [image_directory],
                    [image_directory],
                )
            )

    return patients


@jit(void(int32[:], int32), nopython=True)
def shuffle(array: np.ndarray, num_times: int) -> None:
    """
    Shuffle the array.

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


def generate_ids(seed: int, length: int) -> np.ndarray:
    """
    Randomly generate ids.

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


def anonymize_id_patients(patients: List[Patient]) -> None:
    """
    Generate an anonymized id for each patient.

    :param patients: list of Patient objects
    :return: None
    """
    seed = 0
    # generate enough numbers in order to have a "random" pattern
    length = max(len(patients * 10), 1000)
    ids = generate_ids(seed, length)

    for i, patient in enumerate(patients):
        patient.generate_anonymized_id(ids[i])


def anonymize_patient(
    output_dir: Path, parallel: bool, destination_directory: bool, patient: Patient
) -> None:
    """
    Generate an anonymized id for each patient.

    :param output_dir: Path of the output directory
    :param parallel: use CPU multithreading
    :param destination_directory: anonymize only the destination directory (bool)
    :param patient: Patient to be anonymized
    :return: None
    """
    patient.anonymize(output_dir, parallel, destination_directory)


def anonymize_patients(
    output_dir: Path, patients: List[Patient], parallel: bool, destination_dir: bool = False
) -> None:
    """
    Generate an anonymized id for each patient.

    :param output_dir: Path of the output directory
    :param patients: list of Patient objects
    :param parallel: use CPU multithreading
    :param destination_dir: anonymize only the destination directory (bool)
    :return: None
    """
    if parallel:
        num_threads = max(len(patients), 1)
        # Somehow multiprocessing.pool.ThreadPool is faster with just a few threads
        # and multiprocessing.pool.Pool is significantly faster with many threads
        if num_threads >= 8:
            # multiprocessing.pool.Pool crashes with too many threads
            with Pool(min(num_threads, cpu_count())) as p:
                p.map(partial(anonymize_patient, output_dir, parallel, destination_dir), patients)
        else:
            with ThreadPool(num_threads) as p:
                p.map(partial(anonymize_patient, output_dir, parallel, destination_dir), patients)
    else:
        for patient in patients:
            anonymize_patient(output_dir, parallel, destination_dir, patient)


def read_patients(input_dir: Path) -> List[Patient]:
    """
    Read patients information.

    :param input_dir: Path of the input directory
    :return: list of patients
    """
    lookup_directories = get_directories(input_dir)

    patients = get_patients(lookup_directories)

    return patients


def write_conversion_table(output_directory: Path, patients: List[Patient]) -> None:
    """
    Write all patient information to a csv file, in order to be able to de-anonymize data.

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
                "Cannot find a unique name for the conversion table."
                + " Aborting write_conversion_table..."
            )
            return

    df.to_csv(output_directory / csv_name, index=False)
