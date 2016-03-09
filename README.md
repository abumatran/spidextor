# Spidextor

Spidextor is a simple glueing script for running Bitextor (https://sourceforge.net/projects/bitextor/), a bitext extraction tool, on the output of SpiderLing (http://corpus.tools/wiki/SpiderLing), a crawler focused on text.

The two dependcies are Python<=2.7 and make.

You should first edit the config.py file with your own parameters.

Next you should feed the prevert format from SpiderLing (the result of physical deduplication obtained by util/remove_duplicates.py) to spiderling2bitextor.py. It will organise data by domain and keep only those domains in which data in both languages was found. It is written in bitextor_output/ with a '.lett.gz' extension.

The final step of spiderling2bitextor.py is running bitextor_output/Makefile. It controls the job scheduling of Bitextor over the prepared data.
