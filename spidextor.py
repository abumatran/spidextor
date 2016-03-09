#!/usr/bin/python

import sys
import base64
import hashlib
import re
import gzip
from collections import Counter
import os
import config
import argparse

reload(sys)
sys.setdefaultencoding("UTF-8")

def geturl(str):
  return re.search(r' url="(.+?)"',str).group(1)

domain_re=re.compile(r'https?://[^/]*?([^\./]+'+'('+'|'.join(config.tld_suffixes).replace('.','\.')+'))[$/:]')

def getdomain(url):
  domain=domain_re.search(url)
  if domain==None:
    return
  else:
    return domain.group(1)

def getlang(str):
  return str.split(' '+config.language_attribute+'="')[1].split('"')[0]

def langcode(lang):
  if lang in config.lang_equiv:
    return config.lang_equiv[lang]

def getchars(str):
  return int(str.split(' chars="')[1].split('"')[0].split("+")[0])

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)    
    
def generate_docs(input):
  output_list = []
  seen_md5 = {}
  skip=False
  for i in input:
    if i.startswith("<doc "):
      skip=False
      output_list = []
      c = hashlib.md5()
      url = geturl(i)
      domain = getdomain(url)
      if domain==None:
        skip=True
        continue
      elif domain in config.blacklisted_domains:
        skip=True
        continue
      lang = langcode(getlang(i))
      if lang not in config.language_codes:
        skip=True
    elif i.startswith("<gap"):
      output_list.append(" "*getchars(i))
      c.update(output_list[-1])
    elif i.startswith("</doc>"):
      if not c.hexdigest() in seen_md5 and not skip:        
        seen_md5[c.hexdigest()] = 1
        ol = []
        ol.append("{0}\t{1}\ttext/html\tcharset=utf-8\t{2}".format(domain, lang, url))  
        ol.append("\t")
        docstr = "".join(output_list)
        ol.append(base64.b64encode(docstr))
        ol.append("\t")
        ol.append(base64.b64encode(remove_tags(docstr)))
        ol.append("\n")
        yield "".join(ol)
      output_list = []
    else:
      output_list.append(i)
      c.update(i)
  return
  
def generate_lett(input, directory):
  nlines = 0
  for i in generate_docs(input):
    parts = i.split("\t")
    filename = "{0}.lett.gz".format(parts[0])
    output = gzip.open(directory+"/"+filename, "a")
    output.write("\t".join(parts[1:]))
    output.close()
    nlines += 1
    if nlines %10000 == 0:
      print nlines

def clear_files(directory, threshold):
  for (dirpath, dirnames, filenames) in os.walk(directory):
    for i in filenames:
      if i.endswith(".lett.gz"):
        file = gzip.open(dirpath+"/"+i, "r")
        counter = Counter()
        for j in file:
          parts = j.split("\t")
          counter[parts[0]] += 1
        file.close()
      
        mylist = counter.most_common(2)
        if len(mylist) == 1:
          os.unlink(dirpath+"/"+i)
        elif mylist[0][1] < threshold or mylist[1][1] < threshold:
          os.unlink(dirpath+"/"+i)
        else:
          print "Preserving ", i, mylist

def generate_makefile(directory):
  makefile = """
LANG1 := {0}
LANG2 := {1}
VOCABULARY := {2}
export PATH := {3}:$(PATH)
export LD_LIBRARY_PATH := {3}/../lib
.PRECIOUS: %.align %.aseg %.idx %.ridx1 %.ridx2 %.ridx1df %.ridx2f %.adoc %.cta

objs = {4}

all: $(objs)

%.${{LANG1}}.txt: %.cta
	cut -f3 $< >$@

%.${{LANG2}}.txt: %.cta
	cut -f4 $< >$@
	
%.doc: %.cta
	cut -f1,2 $< |sort|uniq -c >$@

%.tmx: %.cta
	bitextor-buildTMX --lang1 ${{LANG1}} --lang2 ${{LANG2}} <$< >$@

%.cta: %.aseg
	bitextor-cleantextalign $< >$@
	
%.adoc: %.align hunaligndic
	bitextor-score-document-alignment -d hunaligndic -t . --lang1 ${{LANG1}} --lang2 ${{LANG2}} <$(word 1,$^) >$@

%.aseg: %.align hunaligndic
	bitextor-align-segments -d hunaligndic -t . --lang1 ${{LANG1}} --lang2 ${{LANG2}} <$(word 1,$^) >$@

hunaligndic: ${{VOCABULARY}}
	tail -n+1 $< |gawk '{{print $$2 " @ " $$1}}' >$@

%.align: %.lettr %.ridx1df %.ridx2df
	bitextor-align-documents -l $< -n 0 -r /dev/null $(word 2,$^) $(word 3,$^) >$@
       
%.ridx1df: %.ridx1 %.lettr
	bitextor-distancefilter -l $(word 2,$^) $< >$@

%.ridx2df: %.ridx2 %.lettr
	bitextor-distancefilter -l $(word 2,$^) $< >$@

%.ridx1: %.idx 
	bitextor-idx2ridx -d ${{VOCABULARY}} --lang1 ${{LANG1}} --lang2 ${{LANG2}} $< >$@
	
%.ridx2: %.idx
	bitextor-idx2ridx -d ${{VOCABULARY}} --lang1 ${{LANG2}} --lang2 ${{LANG1}} $< >$@

%.idx: %.lettr
	bitextor-lett2idx -m 15 $< >$@

%.lettr: %.lett.gz
	zcat $< | bitextor-lett2lettr >$@
"""
  
  makefile_line = []  
  for i in config.output_formats:
    if i == "tmx":
      makefile_line.append("$(patsubst %.lett.gz,%.tmx,$(wildcard *.lett.gz))")
    elif i == "txt":  
      makefile_line.append("$(patsubst %.lett.gz,%.{0}.txt,$(wildcard *.lett.gz))".format(config.language_codes[0]))
      makefile_line.append("$(patsubst %.lett.gz,%.{0}.txt,$(wildcard *.lett.gz))".format(config.language_codes[1]))
    elif i == "doc":
      makefile_line.append("$(patsubst %.lett.gz,%.doc,$(wildcard *.lett.gz))")
  
  fd = open(directory+"/Makefile", "w")
  fd.write(makefile.format(config.language_codes[0], config.language_codes[1], config.vocabulary, config.bitextor_path, " ".join(makefile_line)))
  fd.close()


def run_make(directory, parallel_tasks):
  cwd = os.getcwd()
  try:
    os.chdir(directory)
    os.system("make -j{0}".format(parallel_tasks))
  finally:
    os.chdir(cwd)

def do_main():
  parser = argparse.ArgumentParser(description='Spidextor: the glue for SpiderLing and Bitextor.')
  parser.add_argument('-d', '--output-dir', dest="outdir", default=config.output_directory, metavar="DIR")
  parser.add_argument('prevert',metavar='spiderling.prevert',nargs='?',help='Physically deduplicated spiderling output. If undefined, the script will read from STDIN.',default=None)
  options=parser.parse_args()
  if options.prevert==None:
    input = sys.stdin
  else:
    input=open(options.prevert,'r')
  
  if options.outdir != ".":
    if not os.path.exists(options.outdir):
        os.makedirs(options.outdir)
  
  generate_lett(input,options.outdir)
  clear_files(options.outdir, config.min_docs)
  generate_makefile(options.outdir)
  run_make(options.outdir, config.n_jobs)

    
if ( __name__ == "__main__"):
  do_main()
