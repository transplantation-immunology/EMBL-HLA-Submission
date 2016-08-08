#EMBL-HLA-SUBMISSION
A tool for generating an EMBL-formatted submission of a standard novel HLA allele. 

##Run using Python
Run this program using standard python call:
$python AlleleSubmissionEMBL.py

##To configure Anaconda:
Anaconda uses separate environments to run your programs in.
Install Anaconda for python 2.7.
https://www.continuum.io/downloads
To set up the environment in anaconda, run this in console:
$conda create --name AlleleSubEnvironment biopython

##Run using a bash or .bat script using anaconda
You can execute the following scripts to run the tool inside of Anaconda:
Linux/Mac:
bash Run_allele_submission.sh
Windows:
Run_allele_submission.bat

Input data sequence consists of 
1) 5' UTR 
2) An odd number of Exons, with an Even number of introns between them.  
3) 3' UTR

Introns, Exons, and UTRs are to be specified using capital or lowercase letters.  
Exons are capital, while introns and UTRs are lowercase.

Like this:

fiveprimeutrEXONONEintrononeEXONTWOintrontwoEXONTHREEthreeprimeutr

agctagctagctAGCTAGCtagctagctAGCTAGCtagctagctAGCTAGCTAgctagctagctag

All spaces, tabs, and newlines are not interpreted by this program,  They are removed.
If you wish, you may use those characters for more convenient visualization of splice sites:
agctagctagct
AGCTAGC
tagctagct
AGCTAGC
tagctagct
AGCTAGCTA
gctagctagctag

For more information on EMBL's ENA format:

http://www.ebi.ac.uk/ena/submit/sequence-submission

http://www.ebi.ac.uk/ena/submit/entry-upload-templates\n
ftp://ftp.ebi.ac.uk/pub/databases/embl/doc/usrman.txt

ftp://ftp.ebi.ac.uk/pub/databases/embl/doc/FT_current.html

http://www.ebi.ac.uk/ena/software/flat-file-validator
