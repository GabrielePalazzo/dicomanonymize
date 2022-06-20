"""Test script."""

import sys
from pathlib import Path
from os import listdir
from pydicom import dcmread

given_names = ["Mario", "Antonio"]
family_names = ["Rossi", "Verdi"]
patient_ids = ["123456", "286249"]

VALUES_TO_ANONYMIZE = [
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "PatientSex",
    "PatientAge",
    "AcquisitionDate",
    "SeriesDate",
    "StudyDate",
    "ContentDate",
    "StudyTime",
    "SeriesTime",
    "AcquisitionTime",
    "ContentTime",
    "AccessionNumber",
]


def control_image(image_path):
    ds = dcmread(image_path)
    for val in VALUES_TO_ANONYMIZE:
        try:
            assert ds[val].value not in given_names
            assert ds[val].value not in family_names
            assert ds[val].value not in patient_ids
        except Exception:
            pass


def control_study(path, directories):
    for directory in directories:
        # patient directories must not contain patient names
        for name in family_names:
            assert name not in directory
        for name in given_names:
            assert name not in directory

        for image in listdir(path / directory):
            control_image(path / directory / image)


#if __name__ == "__main__":
def test_anonymization():

    #test_dir = (Path.cwd() / sys.argv[0]).parent
    test_dir = Path(__file__).parent

    anonymized_dir = test_dir# / "test"

    sub_dirs = listdir(anonymized_dir)
    try:
        sub_dirs.remove("__pycache__")
    except ValueError:
        pass

    for d in sub_dirs:
        # patient directories must not contain patient names
        for family_name in family_names:
            assert family_name not in d
        try:
            dirs = listdir(anonymized_dir / d)
            control_study(anonymized_dir / d, dirs)
        except Exception:
            # csv files are not directories
            # everything else must be a directory
            assert d.startswith("Anonymization") is True
            assert d.endswith(".csv") is True

    print("Passing")
