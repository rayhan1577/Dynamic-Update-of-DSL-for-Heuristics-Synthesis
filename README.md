# Dynamic-Update-of-DSL-for-Heuristics-Synthesis
# Overview
**Idea to update the DSL dynamically for heuristics Synthesis. This project was completed as course project under supervision of Dr. Levi Lelis.**
(This is not the exact implementation of the papers)
---
n this project, we implemented a methodology where the DSL will be updated dynam-
ically based on the evaluation score of the generated heuristics. That is if a heuristics has
a better evaluation score, we add that heuristics to our DSL and restart the search.This
provides a great advantage. That is we can combine strong heuristics among themselves and
with other non terminal nodes in the first few iterations of the search. Thus we can get a
heuristics with larger AST size by generating few programs. The advantage of this approach
is, we don’t have to evaluate all the programs to reach a program of large AST size.

---


# Set Up
```
# Setup python virtual environment
$ virtualenv venv --python=python3
$ source venv/bin/activate

# clone the repo
$git clone https://github.com/rayhan1577/Heuristics_synthesis.git

# change directory to the repo where we have requirements file
$ cd Heuristics_synthesis
$ cd Codes

```
# Execute
```
$ ./run_synthesis.sh
```


# Report

Results and discussions are available at Report.pdf


# Contributor
---
- Rayhan Kabir (rayhan.kabir@ualberta.ca)
---
