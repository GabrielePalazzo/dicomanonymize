from dataclasses import dataclass


@dataclass
class Patient:
    first_name: str
    last_name: str
    patient_id: str
    anonymized_id: str
    directories: list
