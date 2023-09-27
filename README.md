# CrosswordAI

How might you go about generating a crossword puzzle? Given the structure of a crossword puzzle (i.e., which squares of the grid are meant to be filled in with a letter), and a list of words to use, the problem becomes one of choosing which words should go in each vertical or horizontal sequence of squares. We can model this sort of problem as a constraint satisfaction problem. 

This is an AI program that generates crossword puzzles, using a constraint satisfaction problem model with node consistency, arc consistency, and backtracking search.

<img src="output.png" alt="crossword">

[View the full assignment description on CS50's OpenCourseWare](https://cs50.harvard.edu/ai/2020/projects/3/crossword/)

## How to Use

Follow these steps to run the CrosswordAI program:

1. **Requirements:** Ensure you have Python 3 installed on your system.

2. **Install Dependencies:** Install the required Python packages, including Pillow (for generating image representations of crossword puzzles):

   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run the Program:** Execute the `generate.py` script, providing the paths to the crossword structure and word list files as arguments. Optionally, you can specify an output image file for the generated crossword puzzle:

   ```bash
   python generate.py data/structure1.txt data/words1.txt output.png
   ```
