# Bechdal Test on Movie Scripts

This repo applies [Bechdal test](https://www.wikiwand.com/en/Bechdel_test) to movie scripts from IMSDB website.

The code is divided into the following files:

- **IMSDB_Parser.py**:  
    A parser for IMSDB website, it provides helpful functions to:
        - Scrape movies' scripts from IMSDB website.
        - Extracts scenes and characters from movie script in plain text  
        
    
- **BechdelTest.ipynb**:  
    IPython notebook to perform bechdal test on the parsed movie scenes,
        - Extracts first names.
        - Guesses their gender.
        - Applies Bechdal test on scene level:  
            check if there are at least two women talking to each other without the presence of a man in the scene.  
              

- **AnalysingBechdelResults.ipynb**:  
    Plots analyses of Bechdal test over time.