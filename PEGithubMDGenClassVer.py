"""
This is a fairly basic scraper built from BeautifulSoup4 designed to
pull problem pages from projecteuler.net and build a markdown file
from them. Naturally this is not a very general script.

Some omissions (for the sake of simplicity) include:
- Does not bother with bold or italics or other similar formattings
- Uses characters '^' and '_' to denote super and subscripts respectively
- Utilises a bare minimum of formatting for tables

This script being for my personal use it also organises the .py and
.txt files associated with a given problem. It creates a subdirectory
for each problem, copies the .py file if there is a comment containing
'CORRECT', removes the answer from the comment, and strips the problem
description from the .py file as the README.md file will contain it
instead. (There are option flags for overriding files and filtering
the answer and description.)

Problem .py files are stipped of their answers out of respect for the
owners/operators of Project Euler, as they request users do not
publish answers.

A delay of 3sec is implemented between each problem it handles if
a markdown file was successfully created. This is to prevent spamming
of the Project Euler site as a courtesy.

"""

import sys
sys.path.insert(0,"/home/dco/virtenvBS4/lib/python3.5/site-packages")
import os
import shutil
import fnmatch

import requests
import time
from bs4 import BeautifulSoup
from bs4 import NavigableString

class HTMLParser:
    working_dir = "ProjectEulerSolutions/"
    base_URL = "https://projecteuler.net/"
    post_data = "problem"
    root_path = "/home/dco/PythonProjects/"
    
    def __init__(self, override_py = False, override_md = False, filter_ans = True, filter_desc = True):
        self.override_python = override_py
        self.override_markdown = override_md
        self.filter_answers = filter_ans
        self.filter_description = filter_desc
        self.PEproblem_list = self.findFile('PE*.py', self.root_path)
        self.PEproblem_list = ['PE45-TriangularPentagonalHexagonal.py']

    # File helper functions
    def findFile(self, pattern, path):
        result = []
        for file in os.listdir(path):
            if fnmatch.fnmatch(file, pattern):
                result.append(file)
        return result

    def readFileLine(self, file):
        with open(file) as file:
            for line in file:
                yield(line)

    def checkProblemCompletion(self, source_file):
        with open(source_file) as file:
            for line in file:
                if line.find("CORRECT") != -1:
                    return True
        return False

    def copyPEPyFile(self, source_file, destination_file):
        header = "PROJECT EULER PROBLEM"
        with open(destination_file, 'w') as destination:
            source_lines = readFileLine(source_file)
            line = ''
            filtered_desc = False
            while True:
                try:
                    line = next(source_lines)
                    if line == '"""\n' and not filtered_desc and self.filter_description:
                        line = next(source_lines)
                        if line.find(header) != -1:
                            destination.write("# " + line)
                            line = next(source_lines)
                            while line != '"""\n':
                                line = next(source_lines)
                            filtered_desc = True
                    elif line.find("CORRECT") != -1 and self.filter_answers:
                        pass
                    else:
                        destination.write(line)
                except StopIteration:
                    break


    # URL helper functions
    def digits(self, str_x):
        out_s = ''
        for s in str_x:
            if s in "0123456789":
                out_s += s
        return(out_s)


    # Tag to Markdown parsing helper functions
    def parseP(self, content):
        self.parseLink(content)
        self.parseBR(content)
        self.parseSub(content)
        self.parseSuper(content)

    def parseLink(self, content):
        links = content.select('a')
        for link in links:
            href = str(link['href'])
            text = str(link.text)
            link.replace_with("["+text+"]("+href+")")

    def parseBR(self, content):
        BRs = content.select('br')
        for BR in BRs:
            BR.replace_with("\n")

    def parseSub(self, content):
        subscripts = content.select('sub')
        for subscript in subscripts:
            text = subscript.text
            subscript.replace_with("_" + text)

    def parseSuper(self, content):
        superscripts = content.select('sup')
        for superscript in superscripts:
            text = superscript.text
            superscript.replace_with("^" + text)

    def parseTable(self, content, lines):
        rows = content.select('tr')
        for row in rows:
            new_text = ""
            cells = row.select('td')
            for i,cell in enumerate(cells):
                text = cell.text
                if text and text.strip():
                    if i == 0:
                        new_text += text
                    else:
                        new_text += " | " + text
            new_text += "\n"
            row.replace_with(new_text)
            line = "\n" + str(row.text) + "\n"
            lines.append(line)

    def parseIMG(self, img_content):
        return('![]('+img_content+')')


    # Main execution script
    def execute(self):
        for problem_str in self.PEproblem_list:
            print("{} found in {}.".format(problem_str, self.root_path))
            problem_number = self.digits(problem_str.split('-')[0])
            source_file = self.root_path + problem_str

            if self.checkProblemCompletion(source_file):
                
                problem_URL = self.base_URL + self.post_data + '=' + problem_number
                sub_dir = "PE" + problem_number + "/"
                sub_path = self.root_path + self.working_dir + sub_dir
                python_filename = sub_path + problem_str

                # Make the appropriate subdir if it DNE
                try: 
                    os.makedirs(sub_path)
                    print("Created subdirectory {} in {}".format(sub_dir, self.root_path))
                except OSError:
                    if not os.path.isdir(sub_path):
                        raise
                    else:
                        print("Subdirectory {} already exists in {}".format(sub_dir, self.root_path))

                
                markdown_filename = sub_path + "README.md"
                markdown_file_exists = os.path.isfile(markdown_filename)

                # Generate markdown
                if not markdown_file_exists or self.override_markdown:
                    print("Pulling data from {}...".format(self.base_URL))
                    r = requests.get(problem_URL)
                    soup = BeautifulSoup(r.content, "html.parser")
                    content = soup.find(id='content')
                    title = content.h2.text

                    body = content.find(class_='problem_content')
                    
                    print("Generating markdown file...")
                    lines = ["# " + title + "\n", "## [Problem " + problem_number + "](" + problem_URL + ")\n"]
                    for tag in body.findChildren():
                        if tag.name == 'p':
                            self.parseP(tag)
                            line = str(tag.get_text()) + "\n"
                            lines.append(line)
                        elif tag.name == 'div':
                            img = tag.img
                            if img:
                                line = self.parseIMG(self.base_URL + tag.img['src']) + "\n"
                                lines.append(line)
                        elif tag.name == 'br':
                            lines.append("\n")
                        elif tag.name == 'table':
                            self.parseTable(tag, lines)
                        
                    with open(markdown_filename,'w') as file:
                        for line in lines:
                            file.write(line)
                else:
                    print("README.md already exists in {}".format(sub_path))

                # Relocate .py file to project-problem directory
                python_file_exists = os.path.isfile(python_filename)
                if not python_file_exists or self.override_python:
                    try:
                        copyPEPyFile(source_file, python_filename)
                        print("Python file created: {}".format(python_filename))
                        print(" Filtered description: {}".format(filter_description))
                        print(" Filtered answer: {}".format(filter_answer))
                    except:
                        print("Error generating python file copy at {}!".format(python_filename))
                else:
                    print("Python file has already been copied to {}".format(sub_dir))

                # Prepare .txt files associated with the problem and copy it to the sub_dir
                leading0s = "".join(['0' for i in range(3 - len(problem_number))])
                text_filenames = self.findFile('p' + leading0s + problem_number + '*.txt', self.root_path)
                
                if len(text_filenames):
                    print("Found the following associated text files:")
                    for f in text_filenames:
                        print("\t{}".format(f))
                        if os.path.isfile(sub_path + f):
                            print("{} already exists in {}".format(f, sub_path))
                        else:
                            shutil.copy2(self.root_path + f, sub_path + f)
                            print("{} copied to {}".format(f, sub_path))


                # If a markdown file was created then wait 3sec before next webscrape
                if not markdown_file_exists:
                    time.sleep(3)
                    
            else:
                print("Problem {} is not marked as a correct solution and has been skipped!".format(problem_number))
                
            
            print()



if __name__ == "__main__":
    parser = HTMLParser()
    parser.execute()
