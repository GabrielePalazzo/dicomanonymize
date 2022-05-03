import sys
from pathlib import Path
from os import listdir

given_names = ["Mario", "Antonio"]
family_names = ["Rossi", "Verdi"]
patient_ids = ["123456", "286249"]


def control_study(path, directories):
    print(path)
    for directory in directories:
        # patient directories must not contain patient names
        for name in family_names:
            assert name not in directory
        for name in given_names:
            assert name not in directory


if __name__ == "__main__":

    test_dir = (Path.cwd() / sys.argv[0]).parent

    anonymized_dir = test_dir / "test"

    sub_dirs = listdir(anonymized_dir)

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
