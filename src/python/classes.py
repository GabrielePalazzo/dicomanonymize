from dataclasses import dataclass


@dataclass
class Patient:
    first_name: str
    last_name: str
    patient_id: str
    directories: list
    anonymized_id: str = ""

    def anonymize(self, index):
        """
        Generate an anonymized id

        :param index: int for the generation of the anonymized id
        :return:
        """

        self.anonymized_id = str(index)
