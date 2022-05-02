from dataclasses import dataclass
from pydicom import dcmread
from os import listdir


VALUES_TO_ANONYMIZE = ["PatientName", "PatientID", "PatientBirthDate", "PatientSex", "PatientAge"]


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

            ds = dcmread(path)
            for val in VALUES_TO_ANONYMIZE:
                ds[val].value = self.anonymized_id
            print(ds)

        images = []
        for d in self.directories:
            files = listdir(d)
            for f in files:
                if f.endswith(".dcm"):
                    images.append(d / f)

            # anonymize all images
            for image in images:
                anonymize_image(image)
                break
        # print(self)

    def last_name(self):
        """
        Patient last name

        :return: str containing patient's last name
        """

        return self.patient_data["PatientName"].family_name.title()
