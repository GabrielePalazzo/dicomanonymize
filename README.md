# dicomanonymize

[![Build Status](https://github.com/GabrielePalazzo/dicomanonymize/workflows/Test/badge.svg?branch=main)](https://github.com/GabrielePalazzo/dicomanonymize/actions)

Python library for dicom image anonymization

Usage:

 - `-h`, `--help`: help message
 - `-i`, `--input_files`: input path for original files
 - `-o`, `--outputh_path`: output path for anonymized files
 - `-s`, `--single_thread`: run in single thread mode

This script reduces execution times using CPU multithreading. You can force it into single thread mode with `-s` argument.

## Install `dicomanonymize`

You can install it from the repository:

```
git clone https://github.com/GabrielePalazzo/dicomanonymize
cd dicomanonymize
pip install --upgrade .
```
