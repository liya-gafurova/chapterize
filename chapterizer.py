import click
import logging
import re

@click.command()
@click.argument('book')
@click.option('--verbose', is_flag=True, help='Get extra information about what\'s happening behind the scenes.')
@click.option('--debug', is_flag=True, help='Turn on debugging messages.')
@click.version_option('0.1')
def cli(book, verbose, debug):
    """ This tool breaks up a book into chapters. 
    """

    if verbose:
        logging.basicConfig(level=logging.INFO)

    if debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.info('Now attempting to break the file %s into chapters.' % book)

    bookObj = Book(book)

class Book(): 
    def __init__(self, filename): 
        self.filename = filename
        self.contents = self.getContents()
        self.lines = self.getLines()
        self.headings = self.getHeadings()
        self.headingLocations = [heading[0] for heading in self.headings]
        self.ignoreTOC()
        logging.info('Heading locations: %s' % self.headingLocations) 
        headingsPlain = [self.lines[loc] for loc in self.headingLocations]
        logging.info('Headings: %s' % headingsPlain) 
        self.chapters = self.getTextBetweenHeadings()
        # logging.info('Chapters: %s' % self.chapters) 
        self.numChapters = len(self.chapters)
        self.writeChapters()

    def getContents(self): 
        """
        Reads the book into memory. 
        """
        with open(self.filename) as f: 
            contents = f.read()
        return contents

    def getLines(self): 
        """ 
        Breaks the book into lines.
        """
        return self.contents.split('\n')

    def getHeadings(self): 

        # Form 1: Chapter I, Chapter 1, Chapter the First, CHAPTER 1
        # Ways of enumerating chapters, e.g. 
        arabicNumerals = '\d+'
        romanNumerals = '(?=[MDCLXVI])M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})' 
        enumeratorsList = [arabicNumerals, romanNumerals, 
                       'the first', # Chapter the First
                       'the last'] # Chapter the Last
        enumerators = '(' + '|'.join(enumeratorsList) + ')'
        chapterLabelList = ['Chapter', 'CHAPTER']
        chapterLabels = '(' + '|'.join(chapterLabelList) + ')'
        form1 = chapterLabels + enumerators

        # Form 2: II. The Mail 
        enumerators = romanNumerals 
        separators = '(\. | )'
        titleCase = '[A-Z][a-z]'
        form2 = enumerators + separators + titleCase

        pat = re.compile('(%s)|(%s)' % (form1, form2))

        headings = [(self.lines.index(line), pat.match(line)) for line in self.lines if pat.match(line) is not None] 

        self.endLocation = self.getEndLocation()

        print('self.endlocation: ', self.endLocation)

        # Treat the end location as a heading. 
        headings.append((self.endLocation, None))

        return headings

    def ignoreTOC(self): 
        """
        Filters headings out that are too close together, 
        since they probably belong to a table of contents. 
        """
        pairs = zip(self.headingLocations, self.headingLocations[1:])
        toBeDeleted = []
        for pair in pairs: 
            delta = pair[1] - pair[0]
            if delta < 4: 
                if pair[0] not in toBeDeleted: 
                    toBeDeleted.append(pair[0])
                if pair[1] not in toBeDeleted: 
                    toBeDeleted.append(pair[1])
        logging.debug('TOC locations to be deleted: %s' % toBeDeleted) 
        for badLoc in toBeDeleted: 
            index = self.headingLocations.index(badLoc)
            del self.headingLocations[index]

    def getEndLocation(self): 
        """
        Tries to find where the book ends. 
        """
        ends = ["End of the Project Gutenberg EBook", 
                "End of Project Gutenberg's"]
        joined = '|'.join(ends) 
        pat = re.compile(joined, re.IGNORECASE)
        endLocation = None
        for line in self.lines: 
            if pat.match(line) is not None: 
                endLocation = self.lines.index(line) 
                self.endLine = self.lines[endLocation] 
                break

        if endLocation is None: # Can't find the ending. 
            logging.info("Can't find an ending line. Assuming that the book ends at the end of the text.")
            endLocation = len(self.lines)-1 # The end
            self.endLine = 'None' 

        logging.info('End line: %s at line %s' % (self.endLine, endLocation)) 
        return endLocation

    def getTextBetweenHeadings(self):
        chapters = []
        lastHeading = len(self.headingLocations) - 1
        for i, headingLocation in enumerate(self.headingLocations):
            if i is not lastHeading: 
                nextHeadingLocation = self.headingLocations[i+1]
                chapters.append(self.lines[headingLocation+1:nextHeadingLocation])
        return chapters

    def zeroPad(self, numbers): 
        """ 
        Takes a list of ints and zero-pads them, returning
        them as a list of strings. 
        """
        maxNum = max(numbers) 
        maxDigits = len(str(maxNum))
        numberStrs = [str(number).zfill(maxDigits) for number in numbers] 
        return numberStrs

    def writeChapters(self): 
        chapterNums = self.zeroPad(range(1, len(self.chapters)+1))
        logging.debug('Writing chapter headings: %s' % chapterNums)
        dir = 'chapters'
        ext = '.txt'
        for num, chapter in zip(chapterNums, self.chapters):
            path = dir + '/' + num + ext
            logging.debug(chapter)
            chapter = '\n'.join(chapter)
            with open(path, 'w') as f: 
                f.write(chapter)

if __name__ == '__main__':
    cli()
