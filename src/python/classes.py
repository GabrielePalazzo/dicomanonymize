from dataclasses import dataclass
from pydicom import dcmread
from os import listdir
import re
import psutil
from multiprocessing import Pool
from functools import partial


VALUES_TO_ANONYMIZE = ["PatientName", "PatientID", "PatientBirthDate", "PatientSex", "PatientAge"]


def anonymize_image(patient, path):
    """
    Anonymize a single image

    :param path: pathlib Path to the image
    :return: None
    """

    ds = dcmread(path)
    for val in VALUES_TO_ANONYMIZE:
        ds[val].value = patient.anonymized_id
    # print(ds)
    temp_dir = path.parent.name.lower()
    temp_dir = re.sub(patient.last_name().lower(), patient.anonymized_id, temp_dir)
    temp_dir = re.sub(patient.given_name().lower(), patient.anonymized_id, temp_dir)
    path = path.parent.parent / temp_dir / path.name

    temp_dir = path.parent.name.lower()
    temp_dir = re.sub(patient.last_name().lower(), patient.anonymized_id, temp_dir)
    path = path.parent.parent.parent / temp_dir / path.parent.name / path.name

    output_path = path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # print("Writing anonymized image", output_path)
    ds.save_as(output_path)


@dataclass
class Patient:
    patient_data: dict
    directories: list
    anonymized_id: str = ""

    def generate_anonymized_id(self, index):
        """
        Generate an anonymized id

        :param index: int for the generation of the anonymized id
        :return: None
        """

        self.anonymized_id = str(index)

    def anonymize(self, parallel=True):
        """
        Anonymize all patient data

        :param parallel: use CPU multithreading
        :return: None
        """

        images = []
        for d in self.directories:
            files = listdir(d)
            for f in files:
                if f.endswith(".dcm"):
                    images.append(d / f)

            # anonymize all images
            if parallel:
                cpu_number = max(psutil.cpu_count() - 2, 1)
                with Pool(cpu_number) as p:
                    p.map(partial(anonymize_image, self), images)
            else:
                for image in images:
                    anonymize_image(self, image)
                # break
        # print(self)

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
