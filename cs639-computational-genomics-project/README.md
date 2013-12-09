# Introduction

Computational Genomics project.

# Team

    Aidan Fowler
    Lavanya Sivakumar
    Kartik Thapar

# Software

The main algorithms and their implementations are located in:

    /code/bin/

## MRJob run

In order to run a lot of our code you must install the `mrjob` python library on your computer. Instructions are located at http://pythonhosted.org/mrjob/.

To generate our linear results for, we used the mrdc3 algorithm as follows:

    python code/bin/mrjob/mrdc3.py < input.txt > output.txt

The input files are strings of lowercase nucleotides. The example data is in folders marked 100.txt ... 1000000.txt. These files are located in the folder:

    /code/results/TestData

## Hadoop Streaming

To run the job on hadoop streaming, simply give the input file in the hadoop file system to the mrdc3 file:

    > code/bin/hadoop-streaming/mrdc3.sh mrdc3.sh /ktsa/input.txt

The output suffix array can be recovered from the file:

    > hadoop cat /ktsa/currentsuffixarray/part-00000

Currently the program has an issue with large data sets as the intermediate suffix array is passed as a command line argument. The fix for this will be posted to the repository soon.

## Generating data for DC3 C++

To generate our data for the C++ implemntation of DC3 algoirhtm run the `a.out` executable as follows:

    /code/results/OriginalDC3-Results/Code/a.out <input.txt >output.txt

with the same files as above.

# Deliverables

The presentation and the report are located at:

    /deliverables/presentation/genomicsPresentation.pdf
    /deliverables/report/report.pdf
