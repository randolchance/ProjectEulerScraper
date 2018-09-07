# Project Euler Scraper and Markdown Generator

This is a fairly basic scraper built from BeautifulSoup4 designed to
pull problem pages from projecteuler.net and build a markdown file
from them. Naturally this is not a very general script.

Some omissions (for the sake of simplicity) include:
* Does not bother with bold or italics or other similar formattings
* Uses characters '^' and '_' to denote super and subscripts respectively
* Utilises a bare minimum of formatting for tables

This script being for my personal use it also organises the .py and
.txt files associated with a given problem. It creates a subdirectory for each problem, copies the .py file if there is a comment containing 'CORRECT', removes the answer from the comment, and strips the problem description from the .py file as the README.md file will contain it instead. (There are option flags for overriding files and filtering the answer and description.)

Problem .py files are stipped of their answers out of respect for the owners/operators of Project Euler, as they request users do not
publish answers.

A delay of 3sec is implemented between each problem it handles if
a markdown file was successfully created. This is to prevent spamming of the Project Euler site as a courtesy.