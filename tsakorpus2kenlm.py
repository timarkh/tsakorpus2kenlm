import os
import re
from json_doc_reader import JSONDocReader
from text_cleaner import TextCleaner


class LanguageProcessor:
    """
    Contains methods for cleaning or enhancing sentences in
    some languages.
    """
    rxNum = re.compile('^[0-9]+$')
    rxLat = re.compile('^[a-z.-]+$')

    def __init__(self, lang):
        self.lang = lang
        self.tc = TextCleaner(lang)

    def clean(self, s):
        """
        Perform basic text cleaning operations.
        """
        return self.tc.clean_text(s)

    def replace_numerals_kpv(self, s):
        if LanguageProcessor.rxNum.search(s) is None:
            return s
        if len(s) == 1:
            if s == '1':
                return 'ӧтик'
            elif s == '2':
                return 'кык'
            elif s == '3':
                return 'куим'
            elif s == '4':
                return 'нёль'
            elif s == '5':
                return 'вит'
            elif s == '6':
                return 'квайт'
            elif s == '7':
                return 'сизим'
            elif s == '8':
                return 'кӧкъямыс'
            elif s == '9':
                return 'ӧкмыс'
        elif s == '10':
            return 'дас'
        elif s == '20':
            return 'кызь'
        elif s == '30':
            return 'комын'
        return s

    def replace_latin(self, s):
        if LanguageProcessor.rxLat.search(s) is not None:
            return ''
        return s

    def replace_abbr(self, s):
        if s == 'кр':
            return 'коми республика'
        if s == 'кг':
            return 'килограмм'
        return s

    def process_word(self, s):
        s = self.clean(s.lower())
        if self.lang == 'kpv':
            s = self.replace_numerals_kpv(s)
            s = self.replace_abbr(s)
            s = self.replace_latin(s)
        return s


class CorpusTransformer:
    """
    Contains methods for transforming tsakorpus JSON files
    into plain text files.
    """
    rxMultipleSpaces = re.compile('  +')

    def __init__(self, input_format='json', lang='kpv', langCode=0,
                 minAnalyzed=0.66, alphabet='[а-яёӧі -]'):
        """
        Only add sentences where the "lang" attribute equals langCode.
        OExclude sentences where the share of analyzed words is less
        than minAnalyzed.
        """
        self.lang = lang
        self.input_format = input_format
        self.langCode = langCode
        self.minAnalyzed = minAnalyzed
        self.lp = LanguageProcessor(self.lang)
        self.iterSent = None
        self.rxAlphabet = re.compile('^' + alphabet + '+$')
        if self.input_format not in ['json', 'json-gzip']:
            print('Format should equal either "json" or "json-gzip".')
        else:
            self.iterSent = JSONDocReader(format=self.input_format)

    def process_sentences(self, fname):
        """
        Iterate over sentences in a JSON file. For each suitable
        sentence, return its normalized text representation.
        """
        for s, bLast in self.iterSent.get_sentences(fname):
            if 'lang' in s:
                langID = s['lang']
            else:
                langID = 0
            if langID != self.langCode:
                continue
            if 'words' not in s or len(s['words']) <= 0:
                continue
            nWords = sum(1 for token in s['words']
                         if token['wtype'] == 'word')
            if nWords <= 0:
                continue
            nAnalyzed = sum(1 for token in s['words']
                            if token['wtype'] == 'word'
                            and 'ana' in token
                            and len(token['ana']) > 0)
            if nAnalyzed / nWords < self.minAnalyzed:
                continue
            sentOut = ''
            for w in s['words']:
                if w['wtype'] != 'word':
                    continue
                if len(w['wf']) == 1 and ('ana' not in w or len(w['ana']) <= 0):
                    # we need as few one-letter words as possible
                    continue
                sentOut += self.lp.process_word(w['wf']) + ' '
            sentOut = CorpusTransformer.rxMultipleSpaces.sub(' ', sentOut.strip())
            if self.rxAlphabet.search(sentOut) is not None:
                yield sentOut
            # else:
            #     print(sentOut)

    def extract_data(self, dir_in, dir_out):
        """
        Read all .json or .json.gz files in the dir_in folder and
        write their sentences to dir_out.
        """
        if dir_out == dir_in:
            return
        filenames = []
        for root, dirs, files in os.walk(dir_in):
            for fname in files:
                if (not ((self.input_format == 'json'
                          and fname.lower().endswith('.json'))
                         or (self.input_format == 'json-gzip'
                             and fname.lower().endswith('.json.gz')))):
                    continue
                fnameFull = os.path.join(root, fname)
                filenames.append((fnameFull, os.path.getsize(fnameFull)))
        if len(filenames) <= 0:
            print('There are no files in this corpus.')
            return
        sentences = []
        nWords = 0
        for fname, fsize in sorted(filenames, key=lambda p: -p[1]):
            print(fname, fsize)
            for s in self.process_sentences(fname):
                if len(s) > 2:
                    sentences.append(s)
                    nWords += s.count(' ') + 1
        fOut = open(os.path.join(dir_out, self.lang) + '.txt', 'w', encoding='utf-8', newline='\n')
        for s in sorted(sentences):
            fOut.write(s + '\n')
        fOut.close()
        print('Conversion complete, ' + str(len(sentences)) + ' sentences written, '
              + str(nWords) + ' tokens total.')


if __name__ == '__main__':
    dirIn = 'corpora/kpv_main'
    dirOut = 'corpora_kenlm/kpv_main'
    # dirIn = 'corpora/kpv_social_media'
    # dirOut = 'corpora_kenlm/kpv_social_media'
    if not os.path.exists(dirOut):
        os.makedirs(dirOut)
    ct = CorpusTransformer(input_format='json-gzip', lang='kpv', alphabet='[а-яёӧі -]')
    ct.extract_data(dirIn, dirOut)
