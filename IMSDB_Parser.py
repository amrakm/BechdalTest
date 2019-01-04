from bs4 import BeautifulSoup
import requests
from collections import defaultdict, Counter
from io import StringIO
import datetime
import re

import logging
logger = logging.getLogger()
logging.basicConfig(filename="parsing.log", level=logging.INFO)



class IMSDB_Parser:
    
    '''
    A parser for IMSDB website. provides helpful functions to extract scenes and characters from movie script in plain text
    
    Attributes
    ----------
    movie_title : string
        
    '''

    
    def __init__(self, movie_title):
        
        script_url = "https://www.imsdb.com"+ '/scripts/' + movie_title.replace(" ", "-") + ".html"
        script_details_url = "https://www.imsdb.com" + "/Movie%20Scripts/" + movie_title.replace(" ","%20")+"%20Script.html"

        self.characters = None
        self.characters_sequence = None
        self.scenes = None
        self.lines = None
        
        try: 
            r  = requests.get(script_url)
            soup = BeautifulSoup(r.text, 'html.parser')
            self.scrtext = soup.find(class_ = 'scrtext')

        except:

            self.scrtext = None
            logger.warning('failed to parse {} movie'.format(movie_title))
            
        try:
            r  = requests.get(script_details_url)
            soup = BeautifulSoup(r.text, 'html.parser')
            movie_info = soup.find(class_= 'script-details').get_text()  
            movie_release_date_lines = movie_info[movie_info.find('Date'):]
            movie_release_date = movie_release_date_lines.split("\n")[0].split(":")[1].strip()
            movie_release_date = datetime.datetime.strptime(movie_release_date, '%B %Y')
            self.release_date = movie_release_date

        except:
            logger.warning('failed to fetch release date for {} movie'.format(movie_title) )
            self.release_date = None
            

        
        if self.scrtext:
            
            self.lines = [line for line in self.scrtext.get_text().split('\n') if len(line.strip()) > 0]
            
            if self.lines:
                
                self.parse_characters()
                self.parse_scenes()
        
    
    def parse_scenes(self):
        '''
        Assign to self
        -------
        scene: list of lists
                list of scenes, each scene is a list of lines
        characters_sequence: list of lists
                contains actors appearing in each scene

        '''

        scenes = [[]]
        characters_sequence = []

        for line in self.lines:
            # append a new scene when any of these scene separators is found
            if line.strip()[:4] in ('INT.', 'EXT.', 'ESP.', 'EST.', 'SFX ', 'SFX:', 'VFX:', 'LATE') or 'CONTINUE' in line:

                scenes.append([line])
                if len(scenes) > 1:
                    # append to the character sequence from the last extracted scene
                    characters_sequence.append(self.who_is_in_the_scene(scenes[-2]))

            else:
                scenes[-1].append(line)

        if len(scenes) > 1:        
            characters_sequence.append(self.who_is_in_the_scene(scenes[-2]))
        
        self.characters_sequence = characters_sequence
        self.scenes = scenes
        
        return


    def clean_character_string(self, x):
        '''
        Remove anything between parentheses and any non alphabetic character
        '''
        character = re.sub(r'''\([^)]*\)''', '',  x).strip('VOICE').strip('\r')          
        return re.sub("[^a-zA-Z]+", '', character.strip())

    def parse_characters(self):

        '''
        Finds all characters in a movie


        Returns
        -------
        characters: set of all characters in the movie

        '''
        characters = []
        
        for line in self.lines:
            if line.strip().isupper() and \
                    line.strip()[:4] not in ('INT.', 'EXT.', 'ESP.', 'EST.', 'SFX ', 'SFX:', 'VFX:') and 'CONTINUED' not in line:
                
                characters.append(self.clean_character_string(line))         
        
        self.characters = set(characters)
        
        return 
    

    def who_is_in_the_scene(self, scene):
        '''
        Finds all characters that appears in a specifc scene

        Parameters
        ----------    
        scene: list 
            list of lines in the scene


        Returns
        -------
        characters_in_the_scene: list
            list of characters appear in this scene

        '''
        characters_in_the_scene = []
        
        for line in scene:
            if line.strip().isupper():
                line_cleaned = self.clean_character_string(line)
                
                if line_cleaned in self.characters and line_cleaned not in characters_in_the_scene:
                    characters_in_the_scene.append(line_cleaned)
                    
        return characters_in_the_scene



    def dialog_from_scene(self, scene):
        '''
        Extract dialog text from scene plain text
        This is done by finding the two most frequent indentations, then select only the second largest indenation

        Parameters:
        ----------
        scene: list
            list of lines in the scene

        Returns:
        -------
        string: extracted dialog as a single string

        '''
        
        non_titles = [line for line in  scene if not line.lstrip()[:2].isupper() and len(line.strip()) != 0]
        
        if non_titles:
            
            most_freq_indentations = sorted(Counter([len(line) - len(line.lstrip()) for line in non_titles]).items(), key=lambda x:-x[0])
            dialog_indentation = most_freq_indentations[-2:][0][0]
            return " ".join([line.strip() for line in non_titles if len(line) - len(line.lstrip()) == dialog_indentation])
        else:
            return ""
       