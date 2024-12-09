# Letters2Words | Jorque, Jungco, Mandal, Odieres

# import necessary Python plug-ins and tools
import pygame
import random
import string
import itertools
from nltk.corpus import words

# The word list where the dictionary is based upon
import nltk

DICTIONARY = set(words.words())

# Constants for the layout
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FONT_SIZE = 28
BLOCK_SIZE = 60
MARGIN = 10
BG_COLOR = (0, 0, 51)
TEXT_COLOR = (255, 255, 255)                # Colors chosen arbitrarily
BLOCK_COLOR = (70, 130, 180)
BLOCK_HIGHLIGHT_COLOR = (100, 149, 237)
BUTTON_COLOR = (200, 50, 50)
BUTTON_HOVER_COLOR = (255, 75, 75)
SHUFFLE_COLOR = (50, 200, 50)
SHUFFLE_HOVER_COLOR = (75, 255, 75)
PROGRESS_BAR_BG = (50, 50, 50)
PROGRESS_BAR_FILL = (0, 255, 0)

background_images = [
    pygame.image.load("images/bg_1.png"),
    pygame.image.load("images/bg_2.png"),
    pygame.image.load("images/bg_3.png"),
    pygame.image.load("images/bg_4.png"),
    pygame.image.load("images/bg_5.png"),
    pygame.image.load("images/bg_6.png"),
    pygame.image.load("images/bg_7.png")
]

level_up_image = pygame.image.load("images/level_up.png")
instruction_image = pygame.image.load("images/intro.png")

pygame.mixer.init()
level_up_sound = pygame.mixer.Sound("music/level_up_mx.mp3")
valid_sound = pygame.mixer.Sound("music/valid_mx.mp3")

# **************************************************************************************************************
#                      L E T T E R    G E N E R A T I O N    F O R    G A M E P L A Y
# **************************************************************************************************************

def generate_letters(level):

    VOWELS = "aeiou"
    
    # Set the number of randomized letters (7-11), vowels (at least 3)
    num_letters = random.randint(7,11)
    num_vowels = random.randint(3, 4)

    # Ensure vowels appear no more than TWICE
    vowels = []
    while len(vowels) < num_vowels:     # While not satisfied
        vowel = random.choice(VOWELS)   # generate a vowel to add
        vowels.append(vowel)
        if vowels.count(vowel) > 2:     # IF one vowel appears TWICE
            vowels.remove(vowel)        # remove from the list

    # Generate consonants based on weighted probability
    less_likely = 'hjkqvwxyz'  # Less likely consonants based on word statistics
    consonant_chance = {l: 0.05 if l in less_likely else 1 for l in string.ascii_lowercase if l not in VOWELS }
                    # Used a dictionary for the weights in randomization below
                    # The weight of the less likely conso. being chosen is 0.05
                    # Else 1 for the rest of the conso.

    remaining_consonants = list(consonant_chance.keys())
        # Generate list of keys from the conso. chance dictionary

    num_consonants = num_letters - num_vowels
        # Number of consonants

    generated_consonants = random.choices(
        remaining_consonants,                                                   # The list of conso. to choose
        weights = [consonant_chance[char] for char in remaining_consonants],    # Weights/ chances of being picked
        k = num_consonants                                                      # The n of conso. to generate   
    )

    # Less likely consonants can only appear once, IF generated
    consonants = []
    less_likely_set = set() # Track the less likely consonants | Sets disallow duplicates
    for l in generated_consonants:
        if l in less_likely:                # IF conso. is less likely
            if l not in less_likely_set:    # IF not in less likely set
                consonants.append(l)        # ADD it to the conso. list
                less_likely_set.add(l)     # ADD to the less likely set so NOT added again
        else:
            consonants.append(l) # IF NOT less likely, add to the conso. list


    # Ensure consonants appear no more than TWICE
    consonants = []
    consonant_count = {}  # How many times the conso. appear using DICT
    for l in generated_consonants:
        # If the consonant is already in the list and appears twice, skip it
        if consonant_count.get(l, 0) < 2:
            consonants.append(l)
            consonant_count[l] = consonant_count.get(l, 0) + 1

    vowels = []
    while len(vowels) < num_vowels:     # While not satisfied
        vowel = random.choice(VOWELS)   # generate a vowel to add
        vowels.append(vowel)
        if vowels.count(vowel) > 2:     # IF one vowel appears TWICE
            vowels.remove(vowel)  

    # Combine vowels and consonants with shuffle
    letters = vowels + consonants
    random.shuffle(letters)

    # Return value of the generated letters for mechanics
    return letters

def calculate_score(word):
    
    # Calculate the score based on the word length.
    
    if len(word) == 1:
        return 0
    elif len(word) == 3:
        valid_sound.play()        
        return 5
    elif len(word) == 4:
        valid_sound.play()        
        return 10
    elif len(word) == 5 or 6:
        valid_sound.play()
        return 25
    else:
        valid_sound.play()
        return 30


def is_valid_word(word, letters):

    # Check if a word is valid: in dictionary and uses only given letters.
    
    word = word.lower()                 # Lowercase the words to stop case sensitivity
    letters_copy = letters.copy()       # Copy a list for the iteration to begin
    if word not in DICTIONARY:
        return False                    # IF word is not in DICT., make it INVALID
    for l in word:                      # IF otherwise:
        if l in letters_copy:           # check if the word is in the generated letters
            letters_copy.remove(l)      # Using the copied list, remove each letter
        else: 
            return False                # IF even one letter is ABSENT, make it INVALID
    return True

def check_for_valid_words(letters):
    
    # Check if the letters generate at least 15 valid words for QoL

    valid_words = set()         # Valid words set to UNABLE duplication
    
    # Check for 3-letter or longer words
    for i in range(3, len(letters) + 1):                    # Start from 3-letter words, 2 and 1 are INVALID
        for word in itertools.permutations(letters, i):     # Permutation of the letters with i length
            word_str = ''.join(word)                        # make the permu. (list) into a string
            if word_str in DICTIONARY:                      #   IF that str is in DICT:
                valid_words.add(word_str)                   #       ADD to the set of valid words
    
    return len(valid_words) >= 15      # Set the number of vald words required; Boolean.

    # Later on in the code, if the func. is FALSE, it regenerates the letters


# **************************************************************************************************************
#                      G A M E     I N T E R F A C E    U S I N G    P Y G A M E 
# **************************************************************************************************************


def get_clicked_block(mouse_pos, letters):
    
    # Get the index of the clicked letter block based on mouse position.
    
    for i, _ in enumerate(letters):
        x = MARGIN + (BLOCK_SIZE + MARGIN) * (i % 10)
        y = 100 + (BLOCK_SIZE + MARGIN) * (i // 10)
        rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
        if rect.collidepoint(mouse_pos):
            return i
    return None


def draw_letters(screen, letters, selected_indices, font):
    
    # Draw the letter blocks on the screen.
    
    for i, letter in enumerate(letters):
        x = MARGIN + (BLOCK_SIZE + MARGIN) * (i % 11)
        y = 100 + (BLOCK_SIZE + MARGIN) * (i // 11)
        color = BLOCK_HIGHLIGHT_COLOR if i in selected_indices else BLOCK_COLOR
        pygame.draw.rect(screen, color, (x, y, BLOCK_SIZE, BLOCK_SIZE))
        text = font.render(letter.upper(), True, TEXT_COLOR)
        text_rect = text.get_rect(center=(x + BLOCK_SIZE // 2, y + BLOCK_SIZE // 2))
        screen.blit(text, text_rect)


def draw_button(screen, font, text, rect, is_hovered, color, hover_color):
    
    # Draw a button on the screen.
    
    button_color = hover_color if is_hovered else color
    pygame.draw.rect(screen, button_color, rect)
    text_surf = font.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)


def draw_progress_bar(screen, x, y, width, height, progress, level):
    
    # Draw a progress bar on the screen.
    
    pygame.draw.rect(screen, PROGRESS_BAR_BG, (x, y, width, height))
    pygame.draw.rect(screen, PROGRESS_BAR_FILL, (x, y, int(width * progress), height))

# **************************************************************************************************************
#                      D I S P L A Y     S C R E E N S
# **************************************************************************************************************

def draw_level_up(screen):
    # LEVEL-UP
    screen.blit(level_up_image, (0, 0))
    pygame.display.flip()
    pygame.time.wait(2000)

def show_instructions(screen, font):
    # Instructions
    screen.blit(instruction_image, (0, 0))
    pygame.display.flip()
    pygame.time.wait(5000)


# **************************************************************************************************************
#                      M A I N     P Y G A M E
# **************************************************************************************************************

def main():
    pygame.init()

    # BG music
    pygame.mixer.music.load("music/bg_mx.mp3")
    pygame.mixer.music.play(-1)

    # Display the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))     
    pygame.display.set_caption("Letters2Words")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, FONT_SIZE)

    level = 1                                       # Starting Level
    score = 0
    reference_score = 0                             # Starting Score
    letters = generate_letters(level)               # Generate Letters
    selected_indices = []                           # Track selected letters
    current_word = ""                               # Track the word FORMED
    words_created = []                              # List of created WORDS
    target_score = 50                               # Points required to level up
    show_instructions(screen, font)                 # Instruction pop-up

    while not check_for_valid_words(letters):       # Ensure that there are enough
        letters = generate_letters(level)           # VALID letters to level-up

    running = True
    while running:
        screen.fill(BG_COLOR)

        screen.blit(background_images[(level - 1) % len(background_images)], (0, 0))

        # Buttons
        quit_button_rect = pygame.Rect(SCREEN_WIDTH - 150, 10, 140, 40)     # Quit Button Location
        shuffle_button_rect = pygame.Rect(SCREEN_WIDTH - 310, 10, 140, 40)  # Shuffle Button Location
        mouse_pos = pygame.mouse.get_pos()                                  # Track Mouse Position
        is_quit_hovered = quit_button_rect.collidepoint(mouse_pos)          # IS mouse hovering QUIT?   
        is_shuffle_hovered = shuffle_button_rect.collidepoint(mouse_pos)    # IS mouse hovering SHUFFLE?

        # Draw progress bar
        progress = (score - reference_score) / (target_score - reference_score)       # Progress towards the target score
        draw_progress_bar(screen, 10, SCREEN_HEIGHT - 30, SCREEN_WIDTH - 20, 20, progress, level)

        # Draw level and score
        level_text = font.render(f"Level {level}", True, TEXT_COLOR)
        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)

        # Draw the word GREEN if VALID; else normal color (WHITE)
        word_color = (0, 255, 0) if is_valid_word(current_word, [letters[i] for i in selected_indices]) else TEXT_COLOR
        word_text = font.render(current_word.upper(), True, word_color)

        # Display level and score on screen
        screen.blit(level_text, (10, 10))
        screen.blit(score_text, (10, 40))

        # Centered current word
        word_text_rect = word_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(word_text, word_text_rect)

        # Draw word tally in the center
        # ONLY generates VALID words
        word_y = 200
        for word in words_created:
            word_surf = font.render(word.upper(), True, TEXT_COLOR)
            word_rect = word_surf.get_rect(center=(SCREEN_WIDTH // 2, word_y))
            screen.blit(word_surf, word_rect)
            word_y += 30

        # Draw letter blocks
        draw_letters(screen, letters, selected_indices, font)

        # Draw buttons, QUIT and SHUFFLE change color when hovered
        draw_button(screen, font, "Quit Game", quit_button_rect, is_quit_hovered, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        draw_button(screen, font, "Shuffle", shuffle_button_rect, is_shuffle_hovered, SHUFFLE_COLOR, SHUFFLE_HOVER_COLOR)

        for event in pygame.event.get():

            # Handle EVENTS
            if event.type == pygame.QUIT:   # IF the QUIT button is clicked = terminate
                running = False

            # Handle Button Clicks
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if is_quit_hovered:
                    running = False         # QUIT if the button is clicked
                elif is_shuffle_hovered:
                    random.shuffle(letters) # SHUFFLE if the SHUFFLE is clicked
                else:
                    # Letter selection and desselection
                    clicked_index = get_clicked_block(event.pos, letters)
                    if clicked_index is not None:
                        if clicked_index in selected_indices:
                            selected_indices.remove(clicked_index)  # Remove letter if already selected
                            current_word = current_word.replace(letters[clicked_index], "", 1)  # Remove letter from current word
                        else:
                            selected_indices.append(clicked_index)  # Add letter to selected list
                            current_word += letters[clicked_index]  # Add letter to current word

            # Handle Keyboard Inputs
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Check if the word is VALID and has length greater than TWO 
                    if is_valid_word(current_word, [letters[i] for i in selected_indices]) and len(current_word) > 2:
                        if current_word not in words_created:           # Prevent duplicates
                            word_score = calculate_score(current_word)  # Calculate word score
                            score += word_score                         # ADD the score
                            words_created.append(current_word)          # Add to the list of created words
                            current_word = ""                           # Reset the current word
                            selected_indices = []                       # Reset the selected indices

                        # Check for level-up
                        if score >= target_score:
                            level_up_sound.play()
                            draw_level_up(screen)               # Level-Up display
                            level += 1                          # ADD 1 level
                            reference_score += 50               # Reference score for progress bar             
                            target_score += 50                  # ADD target score
                            letters = generate_letters(level)   # Generate NEW letters
                            selected_indices = []               # Reset selected indices
                            current_word = ""                   # Reset the current word
                            words_created = []                  # Clear the tally
                    else:
                        current_word = ""                       # Reset current word if INVALID WORD
                        selected_indices = []                   # Reset current indices if INVALID WORD

                elif event.key == pygame.K_BACKSPACE:
                    if current_word:
                        # Remove the last character from the word
                        last_char = current_word[-1]
                        if last_char in letters:
                            idx = [i for i, l in enumerate(letters) if l == last_char and i in selected_indices]
                            if idx:
                                selected_indices.remove(idx[0])
                        current_word = current_word[:-1]

                # Handle letter typing
                elif event.unicode.lower() in letters:
                    typed_letter = event.unicode.lower()
                    for i, l in enumerate(letters):
                        if l == typed_letter and i not in selected_indices:
                            selected_indices.append(i)
                            current_word += typed_letter
                            break

        # Update the display screen; 30 FPS
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


# Run the game
if __name__ == "__main__":
    main()


# - end -