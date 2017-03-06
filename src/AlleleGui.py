# This file is part of EMBL-HLA-Submission.
#
# EMBL-HLA-Submission is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EMBL-HLA-Submission is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with EMBL-HLA-Submission. If not, see <http://www.gnu.org/licenses/>.

# Version 1.0 
SoftwareVersion = "EMBL-HLA-Submission Version 1.0"

import os

import Tkinter, Tkconstants, tkFileDialog, tkMessageBox
from Tkinter import *

from AlleleGenerator import AlleleGenerator
from HLAGene import *

# The AlleleGui class is an extension of Tkinter.  The GUI elements and interactions are specified in this class.
class AlleleGui(Tkinter.Frame):

    # Initialize the GUI
    def __init__(self, root):
        Tkinter.Frame.__init__(self, root)
        root.title("EMBL Novel HLA Allele Submission Tool")
        self.parent = root
        self.initialize()
    
    # Initialize GUI elements
    def initialize(self):

        button_opt = {'fill': Tkconstants.BOTH, 'padx': 35, 'pady': 5}


        self.cellNumInstrText = Tkinter.StringVar()
        self.cellNumInstrText.set('Sample ID:')
        self.inputCellNummer = Tkinter.StringVar()
        self.inputCellNummer.set('11111')

        self.geneInstrText = Tkinter.StringVar()
        self.geneInstrText.set('Gene:')
        self.inputGene = Tkinter.StringVar()
        self.inputGene.set('HLA-C')

        self.alleleInstrText = Tkinter.StringVar()
        self.alleleInstrText.set('Allele:')
        self.inputAllele = Tkinter.StringVar()   
        self.inputAllele.set('C0213ext')     

        #self.inputFeature = Tkinter.StringVar()
        #self.inputFeature.set('AGC[AGT]CCG[GGC]AAT')
        self.featureInstrText = Tkinter.StringVar()
        self.featureInstrText.set('Annotated Sequence:')

        self.outputEMBLSubmission = Tkinter.StringVar()
        self.outputEMBLSubmission.set('Resulting Allele Submission:')

        #Moving this to the bottom
        #Tkinter.Label(self, width=85, height=3, textvariable=self.instructionText).pack()

        Tkinter.Label(self, width=80, height=1, textvariable=self.cellNumInstrText).pack()
        Tkinter.Entry(self, width=15, textvariable=self.inputCellNummer).pack()

        Tkinter.Label(self, width=80, height=1, textvariable=self.geneInstrText).pack()
        Tkinter.Entry(self, width=15, textvariable=self.inputGene).pack()

        Tkinter.Label(self, width=80, height=1, textvariable=self.alleleInstrText).pack()
        Tkinter.Entry(self, width=15, textvariable=self.inputAllele).pack()

        Tkinter.Label(self, width=80, height=1, textvariable=self.featureInstrText).pack()
        
        # Create a frame for the input widget, add scrollbars.
        self.featureInputFrame = Tkinter.Frame(self)

        self.featureInputXScrollbar = Scrollbar(self.featureInputFrame, orient=HORIZONTAL)
        self.featureInputXScrollbar.pack(side=BOTTOM, fill=X)

        self.featureInputYScrollbar = Scrollbar(self.featureInputFrame)
        self.featureInputYScrollbar.pack(side=RIGHT, fill=Y)

        self.featureInputGuiObject = Tkinter.Text(
            self.featureInputFrame, width=80, height=12, wrap=NONE
            , xscrollcommand=self.featureInputXScrollbar.set
            , yscrollcommand=self.featureInputYScrollbar.set
        )

        self.featureInputXScrollbar.config(command=self.featureInputGuiObject.xview)
        self.featureInputYScrollbar.config(command=self.featureInputGuiObject.yview) 

        self.featureInputGuiObject.pack() 
        self.featureInputFrame.pack()

        self.featureInputGuiObject.delete('1.0','end')
        self.featureInputGuiObject.insert('1.0', 'aag\nCGTCGT\nccg\nGGCTGA\naat')

        #Tkinter.Button(self, text='\|/ Generate an EMBL submission \|/', command=self.updateGUI).pack(**button_opt)
        Tkinter.Button(self, text=unichr(8681) + ' Generate an EMBL submission ' + unichr(8681), command=self.updateGUI).pack(**button_opt)

        Tkinter.Label(self, width=80, height=1, textvariable=self.outputEMBLSubmission).pack()

        # Output interface is contained on a frame.
        self.submOutputFrame = Tkinter.Frame(self)

        self.submOutputXScrollbar = Scrollbar(self.submOutputFrame, orient=HORIZONTAL)
        self.submOutputXScrollbar.pack(side=BOTTOM, fill=X)

        self.submOutputYScrollbar = Scrollbar(self.submOutputFrame)
        self.submOutputYScrollbar.pack(side=RIGHT, fill=Y)

        self.submOutputGuiObject = Tkinter.Text(
            self.submOutputFrame, width=80, height=15, wrap=NONE
            , xscrollcommand=self.submOutputXScrollbar.set
            , yscrollcommand=self.submOutputYScrollbar.set
        )

        self.submOutputXScrollbar.config(command=self.submOutputGuiObject.xview)
        self.submOutputYScrollbar.config(command=self.submOutputGuiObject.yview) 

        self.submOutputGuiObject.pack() 
        self.submOutputFrame.pack()

        # This is the directory the python executable is running from.
        # self.idir is used inside the saveSubmissionFile method.
        # Maybe the code should be in there.
        FileAndPath = os.path.abspath(__file__)
        self.idir, self.ifile = os.path.split(FileAndPath)
        
        Tkinter.Button(self, text='Save this submission to my computer', command=self.saveSubmissionFile).pack(**button_opt)
         
        self.instructionText = Tkinter.StringVar()       
        #self.instructionText.set('This tool assumes you are submitting a standard HLA allele.\n'
        #    + 'HLA alleles are assumed to be fully sequenced, including 5\' and 3\' UTRs.\n'
        #    + 'Use capital letters for exons, lowercase for introns & UTRs, like this:\n'
        #    + 'five\'utr EXON1 intron1 EXON2 ... EXON{X} three\'utr\n'
        #    + 'All spaces, tabs, and newlines are discarded and ignored.')
        self.instructionText.set('This tool was developed by the Tissue Typing Laboratory at\nMaastricht University Medical Center.\nFor more information:')
        Tkinter.Label(self, width=85, height=3, textvariable=self.instructionText).pack()
  
  
        # Make a frame for the more-info buttons
        self.moreInfoFrame = Tkinter.Frame(self)
  
        Tkinter.Button(self.moreInfoFrame, text='How to use this tool', command=self.howToUse).grid(row=0, column=0)
        Tkinter.Button(self.moreInfoFrame, text='Contacting or Citing MUMC', command=self.contactInformation).grid(row=0, column=1)
        


        self.moreInfoFrame.pack()


        self.updateGUI()
        
    def howToUse(self):
        # This method should popup some instruction text in a wee window.
        
        #self.instructionText.set('This tool assumes you are submitting a standard HLA allele.\n'
        #    + 'HLA alleles are assumed to be fully sequenced, including 5\' and 3\' UTRs.\n'
        #    + 'Use capital letters for exons, lowercase for introns & UTRs, like this:\n'
        #    + 'five\'utr EXON1 intron1 EXON2 ... EXON{X} three\'utr\n'
        #    + 'All spaces, tabs, and newlines are discarded and ignored.')
        
        tkMessageBox.showinfo('How to use this tool',
            'This software is to be used to create an\n'
            + 'EMBL-formatted submission document,\n'
            + 'which specifies a novel HLA allele,\n'
            + 'including exon/intron annotation.\n\n'       
                       
            + 'This tool assumes you are submitting a\n'
            + 'full length HLA allele.\n'
            + 'HLA alleles should be fully sequenced,\n'
            + 'including 5\' and 3\' UTRs.\n'
            + 'Use capital letters for exons,\n'
            + 'lowercase for introns & UTRs.\n\n'
            
            + 'An example is included in the form,\n'
            + 'Sequences should follow this pattern:\n'
            + '5\'utr EX1 int1 EX2 ... EX{X} 3\'utr\n\n'
            
            + 'All spaces, tabs, and newlines are\n'
            + 'removed and ignored.'
            )
        
    def contactInformation(self):
        # This method should list contact information for MUMC, and a link to the github page.  
        tkMessageBox.showinfo('Contact Information',
            'This software was created at\n'
            + 'Maastricht University Medical Center\n'
            + 'Transplantation Immunology\n'
            + 'Tissue Typing Laboratory.\n'
            + 'by Ben Matern:\n'
            + 'ben.matern@mumc.nl\n\n'
            
            + 'Please send Ben your bioinformatics\n'
            + 'and data related questions.\n\n'
            
            + 'all other inquiries can be directed\n'
            + 'to Marcel Tilanus:\n'
            + 'm.tilanus@mumc.nl\n\n'
            
            + 'This code will be hosted at:\n'
            + 'https://github.com/transplantation-\nimmunology/EMBL-HLA-Submission\n'
            + 'You will find more information on\n'
            + 'EMBL\'s data format on that page.'

            )

    # Ask user for a output file location, and write the EMBL submission to a file.
    # This takes the input from the output field, rather than generate a new submission.
    # So the user can edit the submission before or after saving it.
    def saveSubmissionFile(self):

        self.dir_opt = options = {}
        options['initialdir'] = self.idir
        options['parent'] = self
        options['title'] = 'Specify your output file.'
        outputFileObject = tkFileDialog.asksaveasfile(**self.dir_opt)
        submissionText = self.submOutputGuiObject.get('1.0', 'end')
        outputFileObject.write(submissionText)
        
    # Gather sequence information from the input elements, and generate a text EMBL submission.
    def updateGUI(self):

        allGen = AlleleGenerator()
        roughFeatureSequence = self.featureInputGuiObject.get('1.0', 'end')
        allGen.inputCellNummer = self.inputCellNummer.get()
        allGen.inputGene = self.inputGene.get()
        allGen.inputAllele = self.inputAllele.get()
        allGen.processInputSequence(roughFeatureSequence)
        enaSubmission = allGen.buildENASubmission()
        self.submOutputGuiObject.delete('1.0','end')    
        self.submOutputGuiObject.insert('1.0', enaSubmission) 
