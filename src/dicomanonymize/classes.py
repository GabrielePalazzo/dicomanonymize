"""Patient class and anonymization functions."""

from dataclasses import dataclass
from pydicom import dcmread
from os import listdir
import re
from multiprocessing.pool import ThreadPool
from functools import partial

from pydicom.dataset import Dataset
from pathlib import Path


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
    "ReferringPhysicianName",
]


@dataclass
class Patient:
    """
    Patient.

    patient_data: dictionary containing patient information (dict)
    source_directories: directories where patient files are located (list[Path])
    destination_directories: destinations for converted files (list[Path])
    anonymized_id: anonymized id for the patient (str).
    """

    patient_data: dict
    source_directories: list
    destination_directories: list
    anonymized_id: str = ""

    def generate_anonymized_id(self, index: int) -> None:
        """
        Generate an anonymized id.

        :param index: int for the generation of the anonymized id
        :return: None
        """
        self.anonymized_id = str(index)

    def anonymize(
        self, output_dir: Path, parallel: bool = True, only_directory: bool = False
    ) -> None:
        """
        Anonymize all patient data.

        :param output_dir: output directory
        :param parallel: use CPU multithreading
        :param only_directory: anonymize only the destination directory (bool)
        :return: None
        """

        def anonymize_directory(output_directory: Path) -> Path:
            """
            Anonymize the directory.

            :param output_directory: Path of the output directory
            :return: Path of the anonymized directory
            """
            temp_dir = output_directory.name
            temp_dir = re.sub(self.last_name().lower(), self.anonymized_id, temp_dir.lower())
            temp_dir = re.sub(self.given_name().lower(), self.anonymized_id, temp_dir.lower())
            temp_dir = re.sub("_[0-9]{4}-[0-9]{2}-[0-9]{2}_", f"_{self.anonymized_id}_", temp_dir)
            output_directory = output_directory.parent / temp_dir

            temp_dir = output_directory.parent.name
            temp_dir = re.sub(
                rf"{self.last_name().lower()}(\^|$)",
                rf"{self.anonymized_id}\g<1>",
                temp_dir.lower(),
            )
            output = output_directory.parent.parent / temp_dir / output_directory.name

            return output

        def anonymize_image(
            input_directory: Path, output_directory: Path, only_dir: bool, path: Path
        ) -> None:
            """
            Anonymize a single image.

            :param input_directory: Path of the input directory
            :param output_directory: Path of the output directory
            :param only_dir: anonymize only the destination directory (bool)
            :param path: pathlib Path to the image
            :return: None
            """
            try:
                dicom_slice = dcmread(path)
                if only_dir is False:
                    for val in VALUES_TO_ANONYMIZE:
                        try:
                            dicom_slice[val].value = self.anonymized_id
                        except Exception:
                            pass
                            # print(f"{val} not found in {path}")
                output_path = output_directory / input_directory.parent.name / input_directory.name
                output_path = anonymize_directory(output_path) / path.name
                self.write_image(dicom_slice, output_path)
            except Exception:
                pass
                # print(f"Could not open {path}")

        images = []
        for i, source_directory in enumerate(self.source_directories):
            files = listdir(source_directory)
            for f in files:
                if f.endswith(".dcm"):
                    images.append(source_directory / f)

            # anonymize all images
            if parallel:
                num_threads = max(len(images), 1)
                with ThreadPool(num_threads) as p:
                    p.map(
                        partial(
                            anonymize_image,
                            self.destination_directories[i],
                            output_dir,
                            only_directory,
                        ),
                        images,
                    )
            else:
                for image in images:
                    anonymize_image(
                        self.destination_directories[i], output_dir, only_directory, image
                    )

    def given_name(self) -> str:
        """
        Patient given name.

        :return: str containing patient's given name
        """
        return self.patient_data["PatientName"].given_name.title()

    def last_name(self) -> str:
        """
        Patient last name.

        :return: str containing patient's last name
        """
        return self.patient_data["PatientName"].family_name.title()

    @staticmethod
    def write_image(dataset: Dataset, output_path: Path) -> None:
        """
        Write single dicom image.

        :param dataset: pydicom dataset of the image
        :param output_path: Path of the output image
        :return: None
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # print("Writing anonymized image", output_path)
        dataset.save_as(output_path)
