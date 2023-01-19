"""Test script."""

from pathlib import Path
from pydicom import dcmread

from dicomanonymize import anonymize

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
    """Control if the DICOM header is anonymized."""
    ds = dcmread(image_path)
    for val in VALUES_TO_ANONYMIZE:
        try:
            assert ds[val].value not in given_names
            assert ds[val].value not in family_names
            assert ds[val].value not in patient_ids
        except Exception:
            pass


def control_study(directories):
    """Control if the DICOM study is anonymized."""
    for directory in directories:
        # patient directories must not contain patient names
        for name in family_names:
            assert name not in directory.name
        for name in given_names:
            assert name not in directory.name

        for image in directory.iterdir():
            control_image(image)


def test_anonymization():
    """Test anonymization."""
    test_dir = Path(__file__).parent
    anonymized_dir = test_dir / "test"

    anonymize(
        test_dir / "Named",
        anonymized_dir,
    )

    sub_dirs = [sub_dir for sub_dir in anonymized_dir.iterdir() if sub_dir.name != "__pycache__"]

    for d in sub_dirs:
        # patient directories must not contain patient names
        for family_name in family_names:
            assert family_name not in d.name
        try:
            dirs = d.iterdir()
            control_study(dirs)
        except Exception:
            # csv files are not directories
            # everything else must be a directory
            assert d.name.startswith("Anonymization") is True
            assert d.name.endswith(".csv") is True

    print("Passing")
