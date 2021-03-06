# This file is part of saddle-bags.
#
# saddle-bags is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# saddle-bags is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with saddle-bags. If not, see <http://www.gnu.org/licenses/>.

from sys import exc_info
from os.path import expanduser

from tkinter import messagebox, filedialog, Frame, StringVar, Button, Label, Text, Scrollbar, Toplevel
from tkinter.constants import BOTH, NORMAL, DISABLED, X, Y, BOTTOM, RIGHT, NONE, HORIZONTAL

from saddlebags.IpdSubGenerator import IpdSubGenerator
from saddlebags.IpdSubOptionsForm import IpdSubOptionsForm
from saddlebags.AlleleSubCommon import assignIcon,  showYesNoBox
from saddlebags.HlaSequence import collectAndValidateRoughSequence
from saddlebags.SaddlebagsConfig import assignConfigurationValue, getConfigurationValue
from saddlebags.HlaSequenceException import HlaSequenceException

import logging

# The AlleleGui class is an extension of Tkinter.  The GUI elements and interactions are specified in this class.
class IpdSubGui(Frame):

    # I shouldn't need to write a select-All method but TK is kind of annoying.
    def selectall(self, event):

        event.widget.tag_add("sel","1.0","end")
        
        
    # Initialize the GUI
    def __init__(self, root):
        Frame.__init__(self, root)
        root.title("Create and Save an IPD-IMGT/HLA Sequence Submission")
        self.parent = root

        # Assign the icon of this sub-window.        
        assignIcon(self.parent)

        # Ctrl-A doesn't work by default in TK.  I guess I need to do it myself.
        root.bind_class("Text","<Control-a>", self.selectall)
        
        # To define the exit behavior.  Save the input sequence text.
        self.parent.protocol('WM_DELETE_WINDOW', self.saveAndExit)

        button_opt = {'fill': BOTH, 'padx': 35, 'pady': 5}
        
        # A frame for the Instructions Label.
        self.instructionsFrame = Frame(self)  
        self.instructionText = StringVar()       
        self.instructionText.set('\nThis tool will generate an HLA allele submission for\n'
            + 'the IPD-IMGT/HLA nucleotide database.\n'
            + 'For more information:\n')
        Label(self.instructionsFrame, width=85, height=6, textvariable=self.instructionText).pack()
        self.instructionsFrame.pack(expand=False, fill='both')
        
        # Make a frame for the more-info buttons
        self.moreInfoFrame = Frame(self)
        self.howToUseButton = Button(self.moreInfoFrame, text='How to use this tool', command=self.howToUse)
        self.howToUseButton.grid(row=0, column=0)
        self.exampleButton = Button(self.moreInfoFrame, text='Example Sequence', command=self.sampleSequence)
        self.exampleButton.grid(row=0, column=1)
        self.moreInfoFrame.pack() 
       
        # Create a frame for the input widget, add scrollbars.
        self.featureInputFrame = Frame(self)
        
        self.featureInstrText = StringVar()
        self.featureInstrText.set('Annotated Sequence:')
        self.featureInstrLabel = Label(self.featureInputFrame, width=80, height=1, textvariable=self.featureInstrText).pack()

        self.featureInputXScrollbar = Scrollbar(self.featureInputFrame, orient=HORIZONTAL)
        self.featureInputXScrollbar.pack(side=BOTTOM, fill=X)

        self.featureInputYScrollbar = Scrollbar(self.featureInputFrame)
        self.featureInputYScrollbar.pack(side=RIGHT, fill=Y)

        self.featureInputGuiObject = Text(
            self.featureInputFrame
            , width=80, height=8
            , wrap=NONE
            , xscrollcommand=self.featureInputXScrollbar.set
            , yscrollcommand=self.featureInputYScrollbar.set
        )

        self.featureInputXScrollbar.config(command=self.featureInputGuiObject.xview)
        self.featureInputYScrollbar.config(command=self.featureInputGuiObject.yview) 

        self.featureInputGuiObject.pack(expand=True, fill='both') 
        self.featureInputFrame.pack(expand=True, fill='both')


        # Create  Frame for "Generate Submission" button.
        self.submButtonFrame = Frame(self)
        self.submissionOptionsButton = Button(self.submButtonFrame, text='1) Submission Options', command=self.chooseSubmissionOptions)
        self.submissionOptionsButton.grid(row=0, column=0)
        self.annotateFeaturesButton = Button(self.submButtonFrame, text='2) Annotate Exons & Introns' , command=self.annotateInputSequence)
        self.annotateFeaturesButton.grid(row=0, column=1)
        self.generateSubmissionButton = Button(self.submButtonFrame, text='3) Generate an IMGT/HLA submission', command=self.constructSubmission)
        self.generateSubmissionButton.grid(row=0, column=2)
        self.submButtonFrame.pack()
       
        # Output interface is contained on a frame.
        self.submOutputFrame = Frame(self)
        
        self.outputENASubmission = StringVar()
        self.outputENASubmission.set('Allele Submission Preview:')
        self.outputENALabel = Label(self.submOutputFrame, width=80, height=1, textvariable=self.outputENASubmission).pack()

        self.submOutputXScrollbar = Scrollbar(self.submOutputFrame, orient=HORIZONTAL)
        self.submOutputXScrollbar.pack(side=BOTTOM, fill=X)

        self.submOutputYScrollbar = Scrollbar(self.submOutputFrame)
        self.submOutputYScrollbar.pack(side=RIGHT, fill=Y)

        self.submOutputGuiObject = Text(
            self.submOutputFrame, width=80, height=8, wrap=NONE
            , xscrollcommand=self.submOutputXScrollbar.set
            , yscrollcommand=self.submOutputYScrollbar.set
        )

        self.submOutputXScrollbar.config(command=self.submOutputGuiObject.xview)
        self.submOutputYScrollbar.config(command=self.submOutputGuiObject.yview) 

        self.submOutputGuiObject.pack(expand=True, fill='both') 
        self.submOutputFrame.pack(expand=True, fill='both')

        self.uploadSubmissionFrame = Frame(self)        
        self.saveSubmissionButton = Button(self.uploadSubmissionFrame, text='4) Save Submission to My Computer', command=self.saveSubmissionFile)
        self.saveSubmissionButton.pack(**button_opt)
        # TODO: Enable IPD Upload functionality. Also enable this button.
        self.uploadButton = Button(self.uploadSubmissionFrame, text='5) Upload Submission to IPD-IMGT/HLA', command=self.uploadSubmission, state=DISABLED)
        self.uploadButton.pack(**button_opt)
        self.exitButton = Button(self.uploadSubmissionFrame, text='Exit', command=self.saveAndExit)
        self.exitButton.pack(**button_opt)
        self.uploadSubmissionFrame.pack()
        
        self.pack(expand=True, fill='both')

    def chooseSubmissionOptions(self):
        logging.info ('Opening the IMGT/HLA Submission Options Dialog')
        
        self.disableGUI()
        
        ipdOptionsRoot = Toplevel()
        ipdOptionsRoot.bind("<Destroy>", self.enableGUI)
        IpdSubOptionsForm(ipdOptionsRoot).pack()

        # Set the X and the Y Position of the options window, so it is nearby.  
        ipdOptionsRoot.update()
        windowXpos = str(self.parent.winfo_geometry().split('+')[1])
        windowYpos = str(self.parent.winfo_geometry().split('+')[2])
        newGeometry = (str(ipdOptionsRoot.winfo_width()) + 'x'
            + str(ipdOptionsRoot.winfo_height()) + '+'
            + str(windowXpos) + '+' 
            + str(windowYpos))
        ipdOptionsRoot.geometry(newGeometry)

        #ipdOptionsRoot.interior.update()


        #ipdOptionsRoot.update()

        ipdOptionsRoot.mainloop()
        #ipdOptionsRoot.update()

        
    def sampleSequence(self):
        self.featureInputGuiObject.delete('1.0','end')
        self.featureInputGuiObject.insert('1.0', 'aag\nCGTCGT\nccg\nGGCTGA\naat')
        
        # Clear the password, keep the username
        assignConfigurationValue('ipd_password','')
        
        assignConfigurationValue("allele_name",'Allele:01:02')
        assignConfigurationValue('gene','HLA-C')
        assignConfigurationValue('sample_id', 'Donor_12345')
        assignConfigurationValue('class','1')
        
        assignConfigurationValue('ena_sequence_accession', 'LT123456')
        assignConfigurationValue('ena_release_date', '01/01/2020')
        
        assignConfigurationValue('is_published','0')
        
        assignConfigurationValue('reference_title', 'Published Reference Title') 
        assignConfigurationValue('reference_authors', 'Albert Authorman, Ben Bioinformaticist, Cindy Cell-Culture') 
        assignConfigurationValue('reference_journal', 'Scientific Journal of Research')  
        
        assignConfigurationValue('closest_known_allele', 'HLA-C*01:02:01')
        assignConfigurationValue('closest_allele_written_description', 'This allele has a C->G polymorphism in Exon 1.\nPosition 5 in the coding sequence.\nThis polymorphism is interesting because of science.')
        
        assignConfigurationValue('ethnic_origin', 'Unknown')
        assignConfigurationValue('sex', 'Unknown')
        assignConfigurationValue('consanguineous', 'Unknown')
        assignConfigurationValue('homozygous', 'Unknown')
        
        assignConfigurationValue('lab_of_origin', 'ACME Laboratories')
        assignConfigurationValue('lab_contact', 'Prof. Laura L. Labcontact')
        
        assignConfigurationValue('material_availability', 'No Material Available')
        assignConfigurationValue('cell_bank', 'Not Available')
        
        # A, B, DRB1 are mandatory, the rest are optional.
        # Allele calls are stored in a dictionary. 
        assignConfigurationValue('source_hla', {
            'HLA-A*':'01:01:01:01,02:02:02:02'
            ,'HLA-B*':'03:03:03:03,04:04:04:04'
            ,'HLA-C*':''
            ,'HLA-DRA*':''
            ,'HLA-DRB1*':'05:05:05:05,06:06:06:06'
            ,'HLA-DRB3*':''
            ,'HLA-DRB4*':''
            ,'HLA-DRB5*':''
            ,'HLA-DRB6*':''
            ,'HLA-DRB7*':''
            ,'HLA-DRB8*':''
            ,'HLA-DRB9*':''
            ,'HLA-DQA1*':''
            ,'HLA-DQB1*':''
            ,'HLA-DPA1*':''
            ,'HLA-DPB1*':''        
        })
      
        self.constructSubmission()
        
    # This method should popup some instruction text in a wee window.
    # This should be explicit on how to use the tool.    
    # TODO: Double check the button text. Did I change these buttons?
    def howToUse(self):
        messagebox.showinfo('How to use this tool',
            'This software is to be used to create an\n'
            + 'IPD-IMGT/HLA-formatted submission document,\n'
            + 'which specifies a (novel) HLA allele.\n\n'       
                       
            + 'This tool requires you to submit a\n'
            + 'full length HLA allele, including\n'
            + '5\' and 3\' UTRs.\n\n'
     
            + 'To create an IPD-IMGT/HLA submission:\n\n'
            + '1.) Paste a full-length HLA sequence in\n'
            + 'the Annotated Sequence text area.\n'
            + '2.) Push [Submission Options] and provide\n'
            + 'the necessary sequence metadata.\n'
            + '3.) Push [Annotate Exons & Introns] to\n'
            + 'annotate your exons automatically.\n'
            + '4.) Push [Generate an IPD-IMGT/HLA submission]\n'
            + 'button to generate a submission.\n'
            # TODO: Change these instructions when the submission functionality works.
            #+ '5.) Push [Upload Submission to ENA]\n'
            #+ 'to submit the sequence\n'
            #+ 'using ENA Webin REST interface\n\n'
            
            + 'If exon annotation is not available,\n'
            + 'it may be necessary to annotate manually.\n\n'

            + 'Sequences should follow this pattern:\n'
            + '5\'utr EX1 int1 EX2 ... EX{X} 3\'utr\n\n'  
            
            + 'Use capital letters for exons,\n'
            + 'lowercase for introns & UTRs.\n\n'
            
            + 'Push the "Example Sequence" button to see\n'
            + 'an example of a formatted sequence.\n\n'
            
            + 'More information available\n'
            + 'on the MUMC Github Page:\n'
            + 'https://github.com/transplantation-\n'
            + 'immunology-maastricht/saddle-bags'

            )
        
    # Ask user for a output file location, and write the IPD submission to a file.
    # This takes the input from the output field, rather than generate a new submission.
    # So the user can edit the submission before or after saving it.
    def saveSubmissionFile(self):

        self.dir_opt = options = {}
       
        options['initialdir'] = expanduser("~")
        options['parent'] = self
        options['title'] = 'Specify your output file.'
        options['initialfile'] = 'IPD.HLA.Submission.txt'
        outputFileObject = filedialog.asksaveasfile(**self.dir_opt)
        submissionText = self.submOutputGuiObject.get('1.0', 'end')
        outputFileObject.write(submissionText)
        # TODO: Did I detect any exceptions? Maybe I don't have permission to write that file        
        # I saw an error when i wrote to a network drive once. 
        
    def annotateInputSequence(self): 
        try:
            self.disableGUI()
            self.update()   
            
            # Popup.  This uses NMDP BTM ACT tool to annotate sequences.
            if (messagebox.askyesno('Annotate Exons?'
                , 'This will annotate your exons using the\n'
                + 'NMDP: BeTheMatch Gene Feature\n'
                + 'Enumeration / Allele Calling Tool.\n\n'
                + 'Please verify you have chosen the correct\n'
                + 'HLA Gene Locus in the\n' 
                + 'Submission Options menu.\n\n'
                + 'Do you want to continue?'                
                )):

                roughNucleotideSequence = collectAndValidateRoughSequence(self.featureInputGuiObject)
            
                alleleCallWithGFE = fetchSequenceAlleleCallWithGFE(roughNucleotideSequence, getConfigurationValue('gene'))
                annotatedSequence = parseExons(roughNucleotideSequence, alleleCallWithGFE)
                self.featureInputGuiObject.delete('1.0','end')    
                self.featureInputGuiObject.insert('1.0', annotatedSequence) 
                
                # TODO: I have not implemented this yet.   I want the generated allele description to be optional
                #alleleDescription = getAlleleDescription(alleleCallWithGFE)
                #closestKnownAllele = getClosestAllele(alleleCallWithGFE)
                # Popup.  I can auto-generate an allele description.
                #if (messagebox.askyesno('Use this generated allele description?'
                #    , 'IPD-IMGT/HLA requires a detailed allele\n'
                #    + 'description with listed polymorphisms\n'
                #    + 'from a related allele.\n'
                #    + 'The NMDP: BeTheMatch Gene Feature\n'
                #    + 'Enumeration / Allele Calling Tool\n'
                #    + 'found this allele description:\n\n'
                #    + str(getConfigurationValue('closest_allele_written_description')) + '\n\n'
                #    + 'Would you like to use this allele description\n'
                #    + 'in your submission?'
                #    )):
                        #assignConfigurationValue('closest_allele_written_description', alleleDescription)
                        #assignConfigurationValue('closest_known_allele', closestKnownAllele)
            self.update()
            self.enableGUI()
            
        except Exception:
            messagebox.showerror('Error Annotating Input Sequence.'
                , str(exc_info()))
            raise
        
    def uploadSubmission(self):
        # TODO: Implement this method.
        logging.info ('This functionality is disabled until it works better.')
                      
    # Gather sequence information from the input elements, and generate a text ENA submission.
    def constructSubmission(self):
        try:
        
            roughNucleotideSequence = collectAndValidateRoughSequence(self.featureInputGuiObject)
            
            if (isSequenceAlreadyAnnotated(roughNucleotideSequence)):
                annotatedSequence = roughNucleotideSequence
                
            else:
                if (showYesNoBox('Auto - Annotate Exons?'
                    , 'It looks like your sequence features have not been identified.\n' +
                    'Would you like to annotate using NMDP: BeTheMatch\n' +
                    'Gene Feature Enumeration Tool?')):
                    
                    self.annotateInputSequence()
                    annotatedSequence = collectRoughSequence(self.featureInputGuiObject)
                else:
                    # You chose not to annotate.  Hope this works out for you.
                    annotatedSequence = roughNucleotideSequence
                
            allGen = IpdSubGenerator()
            allGen.sequenceAnnotation = identifyGenomicFeatures(annotatedSequence)

            # Don't assign a sequenceAnnotation anymore. Give it an AlleleSubmission object, like i'm doing in AlleleSubCommon.createIPDZipFile
            FixThisBug
            
            ipdSubmission = allGen.buildIpdSubmission()
                        
            if (ipdSubmission is None or len(ipdSubmission) < 1):
                messagebox.showerror('Empty submission text'
                    ,'You are missing some required information.\n'
                    + 'Try the \'Submission Options\' button.\n')
                
                self.submOutputGuiObject.delete('1.0','end')    
                self.submOutputGuiObject.insert('1.0', '') 
            else:
                self.submOutputGuiObject.delete('1.0','end')    
                self.submOutputGuiObject.insert('1.0', ipdSubmission)
            
        except KeyError:
            messagebox.showerror('Missing Submission Options'
                ,'You are missing some required information.\n'
                + 'Use the \'Submission Options\' button.\n'
                + 'Missing Data: ' + str(exc_info()))
           
        except HlaSequenceException:
            messagebox.showerror('I see a problem with Sequence Format.'
                , str(exc_info()))
           
        except Exception:
            messagebox.showerror('Error Constructing Submission.'
                , str(exc_info()))
            raise       
            
            
            
    def saveAndExit(self):
        assignConfigurationValue('sequence', self.featureInputGuiObject.get('1.0', 'end'))
        self.parent.destroy()
        
        
    def enableGUI(self, event=None):
        self.toggleGUI(True)  
        
    def disableGUI(self):
        self.toggleGUI(False)   
        
    def toggleGUI(self, isEnabled): 
        #logging.info ('Toggling GUI Widgets:' + str(isEnabled))
         
        newState = (NORMAL if (isEnabled) else DISABLED)
        
        # Choosing the widgets individually, this makes the most sense I think.
        self.howToUseButton.config(state=newState) 
        self.exampleButton.config(state=newState)         
        #self.featureInputGuiObject.config(state=newState)
        self.submissionOptionsButton.config(state=newState)
        self.generateSubmissionButton.config(state=newState)
        self.annotateFeaturesButton.config(state=newState)
        self.submOutputGuiObject.config(state=newState)
        #self.uploadButton.config(state=newState)
        self.saveSubmissionButton.config(state=newState)
        self.exitButton.config(state=newState)
        
            

