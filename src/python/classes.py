from dataclasses import dataclass
from pydicom import dcmread
from os import listdir


@dataclass
class Patient:
    first_name: str
    last_name: str
    patient_id: str
    directories: list
    anonymized_id: str = ""

    def generate_anonymized_id(self, index):
        """
        Generate an anonymized id

        :param index: int for the generation of the anonymized id
        :return: None
        """

        self.anonymized_id = str(index)

    def anonymize(self):
        """
        Anonymize all patient data

        :return: None
        """

        def anonymize_image(path):
            """
            Anonymize a single image

            :param path: pathlib Path to the image
            :return: None
            """

        images = []
        for d in self.directories:
            files = listdir(d)
            for f in files:
                if f.endswith(".dcm"):
                    images.append(d / f)
            print(images)

            # anonymize all images
