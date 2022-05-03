from dataclasses import dataclass
from pydicom import dcmread
from os import listdir
import re
from multiprocessing.pool import ThreadPool
from functools import partial


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


@dataclass
class Patient:
    patient_data: dict
    source_directories: list
    destination_directories: list
    anonymized_id: str = ""

    def generate_anonymized_id(self, index):
        """
        Generate an anonymized id

        :param index: int for the generation of the anonymized id
        :return: None
        """

        self.anonymized_id = str(index)

    def anonymize(self, output_dir, parallel=True):
        """
        Anonymize all patient data

        :param output_dir: output directory
        :param parallel: use CPU multithreading
        :return: None
        """

        def anonymize_image(output_directory, path):
            """
            Anonymize a single image

            :param patient: Patient to be anonymized
            :param output_directory: Path of the output directory
            :param path: pathlib Path to the image
            :return: None
            """

            ds = dcmread(path)
            for val in VALUES_TO_ANONYMIZE:
                try:
                    ds[val].value = self.anonymized_id
                except Exception:
                    print(f"{val} not found in {path}")

            output_path = anonymize_directory(path.parent, output_directory) / path.name
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # print("Writing anonymized image", output_path)
            ds.save_as(output_path)

        def anonymize_directory(dir_name, output_directory):
            """
            Anonymize the directory

            :param dir_name: Path of the original directory
            :param output_directory: Path of the output directory
            :return: Path of the anonymized directory
            """

            temp_dir = dir_name.name.lower()
            temp_dir = re.sub(self.last_name().lower(), self.anonymized_id, temp_dir)
            temp_dir = re.sub(self.given_name().lower(), self.anonymized_id, temp_dir)
            temp_dir = re.sub("_[0-9]{4}-[0-9]{2}-[0-9]{2}_", f"_{self.anonymized_id}_", temp_dir)
            dir_name = dir_name.parent / temp_dir

            temp_dir = dir_name.parent.name.lower()
            temp_dir = re.sub(self.last_name().lower(), self.anonymized_id, temp_dir)
            output_path = output_directory / temp_dir / dir_name.name
            return output_path

        def anonymize_destinations(out):
            """
            Anonymize self.destination_directories

            :param out: Path of the output directory
            :return: None
            """

            for i, d in enumerate(self.destination_directories):
                self.destination_directories[i] = anonymize_directory(d, out)

        images = []
        for d in self.source_directories:
            files = listdir(d)
            for f in files:
                if f.endswith(".dcm"):
                    images.append(d / f)

            # anonymize all images
            if parallel:
                with ThreadPool(len(images)) as p:
                    p.map(partial(anonymize_image, output_dir), images)
            else:
                for image in images:
                    anonymize_image(output_dir, image)

        anonymize_destinations(output_dir)

    def given_name(self):
        """
        Patient given name

        :return: str containing patient's given name
        """

        return self.patient_data["PatientName"].given_name.title()

    def last_name(self):
        """
        Patient last name

        :return: str containing patient's last name
        """

        return self.patient_data["PatientName"].family_name.title()
