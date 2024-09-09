import pdfplumber
import re
import math
from langdetect import detect
import os

def open_file_in_same_directory(file_name):
   script_dir = os.path.dirname(os.path.abspath(__file__))
   file_path = os.path.join(script_dir, file_name)
   
   return file_path


class GradeCalculator:
    def __init__(self, pdf_file, use_passed_nonpassed:bool):
        
        self.pdf_file = pdf_file
        self.language = self.detect_language() #Checking language
        
        #Constructing class based on language, and use_passed_nonpassed
        if self.language == "en":
            self.setup_english(use_passed_nonpassed)
            
        elif self.language == "no":
            self.setup_norwegian(use_passed_nonpassed)
        
        #If unsopperted language detected
        else:
            raise ValueError("Unsupported language")
    
    # ----------- Meta functions ------
    def setup_english(self, use_passed_nonpassed:bool):
        self.grades_from_transcript = []
        self.grades_sum = 0
        self.index_keyword_start = "Course Semester Credits Grade A B C D E"
        self.index_keyword_end = "Total:"

        if use_passed_nonpassed == True:
            self.grade_letters = ["A", "B", "C", "D", "E", "F", "Passed", "Not passed"]
            self.grade_values = {'A': 5, 'B': 4, 'C': 3,'Passed':3, 'D': 2, 'E': 1, 'F': 0, 'Not passed':0}
        else:
            self.grade_letters = ["A", "B", "C", "D", "E", "F"]
            self.grade_values = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0}
            
        self.grade_count = {grade: 0 for grade in self.grade_letters}
        
    def setup_norwegian(self, use_passed_nonpassed:bool):
        self.grades_from_transcript = []
        self.grades_sum = 0
        self.index_keyword_start = "Emne Termin poeng Karakter A B C D E"
        self.index_keyword_end = "Sum:"

        
        if use_passed_nonpassed == True:
            self.grade_letters = ["A", "B", "C", "D", "E", "F", "Bestått", "Ikke bestått"]
            self.grade_values = {'A': 5, 'B': 4, 'C': 3,'Bestått':3, 'D': 2, 'E': 1, 'F': 0, 'Ikke bestått':0}
        else:
            self.grade_letters = ["A", "B", "C", "D", "E", "F"]
            self.grade_values = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0}
            
        self.grade_count = {grade: 0 for grade in self.grade_letters}
    
    def get_language(self):
        return self.language
    
    def detect_language(self):
        
        with pdfplumber.open(self.pdf_file) as pdf:
            
            all_text = ""
            
            for page in pdf.pages:
                all_text += page.extract_text()
            
            lang = detect(all_text)
            return lang
       
    # ----------- Calculation ----------
    def grade_to_letter(self,grade):
        for key, value in self.grade_values.items():
            if value == grade:
                return key
        return None 
        
    def extract_text(self):
        with pdfplumber.open(self.pdf_file) as pdf:
            all_text = ""
        
            # Loop through all pages
            for page in pdf.pages:
                page_text = page.extract_text()
                all_text += page_text  # Append the text from each page
        
            # Find the start and end of the required section
            start_index = all_text.find(f"{self.index_keyword_start}")
            end_index = all_text.find(f"{self.index_keyword_end}") 
                        
            #Raise exception if not right format
            if (start_index < 0 or end_index<0):
                raise IndexError("File not an NTNU transcript of records")
            

            #The relevant text
            needed_text = all_text[start_index  : end_index+15]
            return needed_text
    
    def process_text(self, text):
        re.sub(r"(\n)([A-Z]{2,6}\d{3,4})", r"\1\n\2", text)
            
        #Split the courses on newline
        sentences = text.split("\n")
        # print(sentences)
        
        #remove first element if keyword
        if (sentences[0] == self.index_keyword_start):
             sentences = sentences[1:]
             
             
        #Removing last element if it does not contain the total study points
        while sentences and self.index_keyword_end not in sentences[-1]:
            sentences.pop()  # Remove the last element
        
        for course in sentences:
            # print(sentences.split())
            grade = course.split()[-1] #Fetch grade
            self.grades_from_transcript.append(grade) #Append to list of grades from transcript
            
        self.grades_sum = self.grades_from_transcript[-1] #Set sum
        
        # #Bulding dictionary with occurences of each grade letter
        for grade in self.grades_from_transcript:
             if grade in self.grade_letters:
                 self.grade_count[grade] += 1
                
    def calculate_grade_average(self):
        total_sum = 0
        total_count = 0
        grade_average_raw = 0
        grade_average_ceil = 0
        grade_average_ceil_letter = 0
        
        # Loop over the grade_count dictionary
        for grade, count in self.grade_count.items():
            # Add to the total sum (grade value * count of that grade)
            total_sum += self.grade_values[grade] * count
            # Add to the total count
            total_count += count

        # Calculate the average grade
        if total_count > 0:
            grade_average_raw = total_sum / total_count
            # Format the grade average to one decimal place
            grade_average_raw = round(grade_average_raw, 1)
        else:
            grade_average = 0  # Handle case where total_count might be 0

        grade_average_ceil = math.ceil(grade_average_raw)
        grade_average_ceil_letter = self.grade_to_letter(grade_average_ceil)
        
        result = {
            "language": self.language,
            "grade_average_raw": grade_average_raw, 
            "grade_average_ceil": grade_average_ceil, 
            "grade_average_ceil_letter": grade_average_ceil_letter, 
            "study_points": self.grades_sum
        }

        return result
 
    def calculate(self):
        print(f"PDF language detected: {self.language} \n")
        text = self.extract_text()
        self.process_text(text)
        return self.calculate_grade_average()
    
    def result(self, grade_avg_raw, grade_avg_ceil, grade_avg_ceil_letter, study_points):
        if(self.language =="no"):
            print(f"Karaktersnitt: {grade_avg_raw}")
            print(f"Karaktersnitt opphøyd: {grade_avg_ceil}")
            print(f"Karaktersnitt bokstav: {grade_avg_ceil_letter}")
            print(f"Studie poeng: {study_points}")
        else:
            print(f"Grade average: {grade_avg_raw}")
            print(f"Grade average ceiling: {grade_avg_ceil}")
            print(f"Grade average letter: {grade_avg_ceil_letter}")
            print(f"Study points: {study_points}")
            

calculator = GradeCalculator(open_file_in_same_directory("test.pdf"), False)
raw, ceil, letter, study_points = calculator.calculate()
calculator.result(raw, ceil, letter, study_points)

