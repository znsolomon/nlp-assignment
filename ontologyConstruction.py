import re
import os

class ontology:
    def __init__(self,subject):
        self.subject = subject
        self.devs = construct(subject)

#(<h2>.*id=")([A-z]+)
