import functions as func


def anonymize(input_directory, output_directory=None, parallel=True):
    """
    Anonymize patients data

    :param input_directory: Path of the input directory
    :param output_directory: Path of the output directory
    :param parallel: use CPU multithreading
    :return: None
    """

    if output_directory is None:
        output_directory = input_directory

    patients = func.read_patients(input_directory)
    func.anonymize_id_patients(patients)
    func.anonymize_patients(output_directory, patients, parallel)