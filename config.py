###input###
language_codes=['en','sl']                           # language codes, specify 2 only per execution
language_attribute='lang'                            # attribute name carrying the document language information
blacklisted_domains=[]                               # names of domains that should be skipped (like 'arrs.gov.si')

###processing###
n_jobs=16                                            # number of parallel jobs
bitextor_path='/usr/local/bin/'                      # path to bitextor setup
min_docs=1                                           # minimum documents in a particular language per hostname
vocabulary='/home/nikola/tools/spidextor/en-sl.dic'                               # vocabulary, the language codes in the first line should correspond to the language_codes variable

###output###
output_formats=['tmx','txt','doc']                   # any subset of the formats is also allowed
output_directory='/home/nikola/tools/spidextor/spidextor_output/'                   # -d option overrides this value


## internals ##
tld_suffixes = [".si", ".gov.si"]                    # suffixes to be considered as tlds, mainly to take things like .com.hr as tlds
lang_equiv ={"English":"en",
             "Slovene":"sl"}                         # language code equivalences, the keys are language codes from the SpiderLing crawl, the values are Bitextor / vocabulary codes
