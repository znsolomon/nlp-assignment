# nlp-assignment
Code for the NLP (Natural Language Processing) assignment in year 2, term 1 of my Uni degree. Programmed in Python 3.5

Program attempts to extract information from lecture reminder notifications.

File walkthrough:

-academicOntology: Pickled class structure created by ontologyConstruction.py for the tagging of subjects

-assignment.py: Contains the main code for tagging the emails

-assignmentEvaluation.pdf: Written report about the assignment

-departmentOntology.txt: HTML file from which academicOntology was constructed

-evalOutput.txt: Output of evaluation.py, showing how well my data compared with the test data

-evaluation.py: Evaluates my data against the test data

-gazetters: Corpora used in assignment.py

-name_tagger.py: Pre-provided code for tagging names, used in assignment.py

-ontologyConstruction.py: Creates academicOntology file by parsing departmentOntology.txt

-professions.txt: Corpora used in assignment.py

seminar_testdata.zip: Contains test files, is the output location for assignment.py. NOTE: Must be unzipped in this directory before running any program.

-tagfile: Pickled POS tagger, used in assignment.py

-trainPOS.py: Created tagfile

All other files are superflous and can be ignored.
