from PIL import Image, ImageDraw, ImageFont
import io
import os

# Script which contains a list of words, and will convert each one to all ciphers listed and save them as PNGs
# Currently have support for Braille, Morse, Semaphore, and Pigpen
# The formatting is currently difficult, especially morse since words of the same length in character are not
# the same length in morse. We did our best to make the ciphers readable with the settings in FONT_OPTIONS

WORD_LIST = ['HEAD CUSTODIAN', 'LOCOMOTOR MORTIS', 'APPARATION', 'DISAPPARATION', 'UMBRIDGEITIS', 'IGOR KARKAROFF', 'POLYJUICE POTION', 'GINNY POTTER', 'CARTOMANCY', 'CLEANSWEEP ONE', 'NYMPHADORA', 'CHUDLEY CANNONS', 'FIREWHISKY', 'KNEAZLE HAIR', 'REGULUS BLACK', 'INVISIBILITY', 'EXPLODING POTION', 'PUMPKIN PASTY', 'CONJURATION', 'LUDOVIC BAGMAN', 'MOBILICORPUS', 'PROFESSOR BINNS', 'AUNTIE MURIEL', 'POTTERWATCH', 'TAILGROWING HEX', 'REVELIO CHARM', 'PETUNIA EVANS', 'TOUJOURS PUR', 'HALFBLOOD PRINCE', 'THE HOBGOBLINS', 'PARVATI PATIL', 'BARTEMIUS CROUCH', 'NECROMANCY', 'DRAGON BLOOD', 'EUPHEMIA POTTER', 'NURMENGARD', 'EXPECTO PATRONUM', 'AGUAMENTI CHARM', 'VICTOR KRUM', 'ENGORGING CHARM', 'DRAGONHIDE', 'MADAME MAXIME', 'ABRAXAS MALFOY', 'UNCLE VERNON', 'BARTY CROUCH', 'COLLOPORTUS', 'KINGS CROSS', 'EXPLODING SNAP', 'ANIMAGUS POTION', 'CHUCKLE EXTRACT', 'RUNESPOOR EGG', 'TRANSFIGURE', 'HESTIA JONES', 'QUAFFLEPOCKING', 'ILVERMORNY', 'AURORA SINISTRA', 'HALL OF PROPHECY', 'HERBIVICUS CHARM', 'CHEERING CHARMS', 'THE GREY LADY', 'ACROMANTULA EGG', 'HUFFLEPUFF', 'HORNED SERPENT', 'CUSHIONING CHARM', 'DEATHLY HALLOWS', 'EMERALD POTION', 'SELWYN FAMILY', 'PROFESSOR SNAPE', 'ARRESTO MOMENTUM', 'SLEEPING POTION', 'QUIDDITCH CUP', 'PARSELTONGUE', 'FIRE SALAMANDER', 'PORTABLE SWAMP', 'KILLING CURSE', 'HOVERING CHARM', 'SECRET KEEPER', 'MADAM EDGECOMBE', 'HARRYHUNTING', 'UNICORN FOAL', 'CORMAC MCLAGGEN', 'KEVIN ENTWHISTLE', 'INTRUDER CHARM', 'PETER PETTIGREW', 'MADAM PUDDIFOOT', 'HERBICIDE POTION', 'HOGWARTS TRAIN', 'KNOCKBACK JINX', 'BUTTERBEER', 'GRYFFINDOR', 'CALMING DRAUGHT', 'PROFESSOR LUPIN', 'DISSENDIUM', 'LORD VOLDEMORT', 'PERCY WEASLEY', 'DEDALUS DIGGLE', 'DIAGON ALLEY', 'SECTUMSEMPRA', 'SHACKLEBOLT', 'CHEIROMANCY', 'ELIXIR OF LIFE', 'LYCANTHROPY', 'EYEBROW JINX', 'UNPLOTTABLE', 'CORNELIUS FUDGE', 'ORDER OF MERLIN', 'VICTOIRE WEASLEY', 'REVIVING SPELL', 'CHIEF AUROR', 'LEAKY CAULDRON', 'MADAME ROSMERTA', 'ANTITHEFT CHARM', 'OPPUGNO JINX', 'REMEMBERALL', 'MARAUDERS MAP', 'NARCOLEPSY', 'DRAGONOLOGIST', 'VERNON DUDLEY', 'ANCIENT STUDIES', 'TRACE CHARM', 'PROTEGO MAXIMA', 'THIEFS DOWNFALL', 'ENLARGING SPELL', 'THE DARK MARK', 'AQUA VITAE', 'QUIDDITCH TEAM', 'CURSED CHILD', 'STRENGTH POTION', 'THE DEATHSTICK', 'IMPEDIMENT HEX', 'BEZOAR STONE', 'CASSIOPEIA BLACK', 'DOREA BLACK', 'ARCTURUS BLACK', 'THE WIZENGAMOT', 'CHINESE FIREBALL', 'KENMARE KESTRELS', 'REVULSION JINX', 'WITCH WEEKLY', 'MENDING CHARM', 'REPELING SPELL', 'SECRETKEEPER', 'LONGBOTTOM', 'EVERLASTING FIRE', 'HERPO THE FOUL', 'APOTHECARY', 'PARSELMOUTH', 'CONJURATIONS', 'METAMORPHMAGUS', 'AGEING POTION', 'DOLORES UMBRIDGE', 'AUROR MACUSA', 'PIGWIDGEON', 'ROLF SCAMANDER', 'HANNAH ABBOTT', 'NICOLAS FLAMEL', 'THE ELDER WAND', 'DELETRIUS CHARM', 'YOU KNOW WHO', 'ANDROMEDA BLACK', 'THE HANGED MAN', 'DRAGON POX CURE', 'AGE LINE SPELL', 'GAWAIN ROBARDS', 'BROOMSTICKS', 'CROOKSHANKS', 'HIPPOGRIFFS', 'JAMES POTTER', 'STAN SHUNPIKE', 'LIQUID LUCK', 'UNICORN HORN', 'SALAMANDER', 'POLTERGEIST', 'THE FAT FRIAR', 'AUTOANSWER QUILL', 'MORSMORDRE', 'HELGA HUFFLEPUFF', 'MAKING MISCHIEF', 'MADAM POMFREY', 'JEAN GRANGER', 'TICKLING HEX', 'DURSLEYS HOUSE', 'HEALING POTION', 'SWIFTSTICK', 'MEMORY POTIONS', 'WAGGA WAGGA', 'TIMETURNER', 'CHARLIE WEASLEY', 'EVENING PROPHET', 'ZACHARIAS SMITH', 'RONALD WEASLEY', 'HOMENUM REVELIO', 'TICKLING CHARM', 'GROUNDSKEEPER', 'GAMEKEEPER', 'SORCERERS STONE', 'MIRANDA GOSHAWK', 'LISA TURPIN', 'REMUS LUPIN', 'COUNTERCHARM', 'PHINEAS BLACK', 'ONEIROMANCY', 'ALASTOR MOODY', 'UNICORN HAIR', 'BANEBERRY POTION', 'CEDRELLA WEASLEY', 'IMPERIUS CURSE', 'MEDIWIZARD', 'HEAD BOY BADGE', 'EVERCHANGING INK', 'CRUCIATUS CURSE', 'THEODORE NOTT', 'BATHILDA BAGSHOT', 'ALBUS SEVERUS', 'JELLYLEGS JINX', 'OLLIVANDERS', 'WOLFSBANE POTION', 'IGNITION SPELL', 'UNDESIRABLE', 'MEROPE GAUNT', 'BOWTRUCKLE', 'BLOCKING JINX', 'BLUEBOTTLE', 'LOVEGOOD FAMILY', 'BILLIUS WEASLEY', 'FIDELIUS CHARM', 'SERPENTSORTIA', 'PALMREADING', 'FILIUS FLITWICK', 'CLEANING POTIONS', 'DIRK CRESSWELL', 'MAGIZOOLOGIST', 'PHOEBE BLACK', 'CHOKING SPELL', 'QUEEN MAEVE', 'STUNNING SPELL', 'UNICORN BLOOD', 'BASILISK FANG', 'MARVOLO GAUNT', 'EXPELLIARMUS', 'AIDAN LYNCH', 'ISOBEL ROSS', 'CADMUS PEVERELL', 'LEVITATION CHARM', 'KETTLEBURN', 'SCRIMGEOUR', 'HELENA RAVENCLAW', 'BABBITTY RABBITY', 'COUNTERCURSE', 'INCENDIO SPELL', 'THUNDERBOLT', 'SHERBET LEMON', 'DEGNOMING GLOVES', 'ANDROMEDA TONKS', 'DARK WIZARDS', 'BUBBLEHEAD CHARM', 'SHELL COTTAGE', 'ZONKOS JOKE SHOP', 'DEAN THOMAS', 'GREGOROVITCH', 'REG CATTERMOLE', 'WALBURGA BLACK', 'PUDDLEMERE', 'TERRY BOOT', 'THE GREAT HALL', 'CONFUNDUS CHARM', 'AMBROSIUS FLUME', 'MOANING MYRTLE', 'MEMORY POTION', 'THE BURROW', 'VERNON DURSLEY', 'DUNG BEETLE', 'THE MARAUDERS', 'REMEMBRALL', 'TOFFEE ECLAIR', 'TRIWIZARD CUP', 'KNOCKTURN ALLEY', 'COURTROOM TEN', 'TRANSYLVANIA', 'PEPPERUP POTION', 'COUNTERHEX', 'OMNIOCULARS', 'DEATH EATER', 'BIBLIOMANCY', 'BORGIN AND BURKE', 'NUMEROLOGY', 'BUTTERFLY SPELL', 'WANDLESS MAGIC', 'MARY CATTERMOLE', 'POMONA SPROUT', 'OLIVER WOOD', 'HORIZONT ALLEY', 'DUMBLEDORE', 'LOVE POTION', 'GIGGLEWATER', 'DRAGON EGG', 'ARITHMANCER', 'REDUCTOR CURSE', 'DAILY PROPHET', 'PYGMY PUFFS', 'CLEANSWEEP TWO', 'TESSOMANCY', 'DEATHLY HALLOW', 'AVADA KEDAVRA', 'DELUMINATOR', 'ANTONIN DOLOHOV', 'UNSPEAKABLE', 'PROTEAN CHARM', 'MAD EYE MOODY', 'CANARY CREAMS', 'VEELA HAIR', 'DEATH EATERS', 'SEVERUS SNAPE', 'RICTUMSEMPRA', 'ALTHEDAS POTION', 'MY IMMORTAL', 'TERENCE HIGGS', 'OUTSTANDING', 'STRETCHING JINX', 'SCUBASPELL', 'MADAM MALKINS', 'FIREBOLT SUPREME', 'ROMILDA VANE', 'ALASTOR GUMBOIL', 'MAFALDA HOPKIRK', 'PORTRAIT CURSE', 'BARTHOLOMEUS', 'BARTY CROUCH JR', 'HEALING SPELL', 'BOMBARDA MAXIMA', 'DIVINATION', 'VANISHING STAIRS', 'LILY POTTER', 'BOILCURE POTION', 'SHRINKING POTION', 'GINNY WEASLEY', 'AWAKENING POTION']

SEMAPHORE = 'semaphore.ttf'
PIGPEN = 'pigpen.otf'
BRAILLE = 'braille.ttf'
MORSE = 'morse.ttf'

CIPHER_LIST = [SEMAPHORE, PIGPEN, BRAILLE, MORSE
               ]
FONT_DIR = 'fonts'
IMG_DIR = '../encoded_imgs'

# Font Size, Position (x, y)
FONT_OPTIONS = {
    BRAILLE: [40, (125, 75)],
    MORSE: [20, (20, 75)],
    SEMAPHORE: [40, (60, 75)],
    PIGPEN: [40, (125, 75)]
}


def main():
    # Create ../encoded_imgs if it isn't already there.
    if not os.path.exists(IMG_DIR):
        os.mkdir(IMG_DIR)
    for idx, word in enumerate(WORD_LIST):
        # Cut down horizontal space by making each word on its own line.
        word = word.replace(' ', '\n')
        # Generate an image for each cipher
        for cipher in CIPHER_LIST:
            img = Image.new('RGB', (600, 200), (243, 243, 243)) # Slightly off-white background
            d = ImageDraw.Draw(img)
            # apply font with formatting options
            fnt = ImageFont.truetype(os.path.join(FONT_DIR, cipher), FONT_OPTIONS[cipher][0])
            if cipher == SEMAPHORE: # Semaphore in caps shows the letters themselves
                word = word.lower()
            if cipher == MORSE: # Morse only gives spaces between letters if in lowercase
                word = word.lower()
            if 'braille' in cipher: # Braille needs extra space between each line
                word = word.replace('\n', '\n\n')
            x_factor = word.count('\n')
            word_position = (FONT_OPTIONS[cipher][1][0] + x_factor*25, FONT_OPTIONS[cipher][1][1] - x_factor*20)
            d.text(word_position, word, font=fnt, fill=(0,0,0))
            # Create an ID for each word and append the first two letters of the cipher used.
            img.save(os.path.join(IMG_DIR, str(idx).zfill(3) + f'_{cipher[0:2]}.png'), 'png')
        print(idx) # Progress Marker


if __name__ == '__main__':
    main()
