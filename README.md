# Spidextor

Spidextor is a simple glueing tool for running Bitextor (https://sourceforge.net/projects/bitextor/), a bitext extraction tool, on the output of SpiderLing (http://corpus.tools/wiki/SpiderLing), a crawler focused on text.

## Dependencies

The two dependencies are Python<=2.7 and make.

## Running Spidextor

You should first edit the `config.py` file and define your own parameters. Each parameter is followed by an explanatory comment.

Spidextor is run via the `spidextor.py`script. You can get the help via ./spidextor.py -h.

The input format for Spidextor is the "prevert" format from SpiderLing (the result of physical deduplication obtained by the SpiderLings `util/remove_duplicates.py`). It can be given either as an argument or fed to STDIN.

What Spidextor does is the following:
* It organises data by domain, encoding them in the Bitextor format, and keeps only those domains in which data in both languages was found (`.lett.gz` extensions)
* It generates a Makefile and runs it with the predefined number of jobs
* Each job runs the Bitextor pipeline, domain by domain (producing `.lettr`, `.idx`, `.ridx1` and `.ridx2`, `.ridx1df` and `.ridx2df`, `.align`, `.aseg` files)
* The results are can be found in the output directory, organised by domain in the predefined formats
