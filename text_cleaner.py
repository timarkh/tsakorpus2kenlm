import re
import copy
import html


class TextCleaner:
    """
    Contains methods for cleaning a string from things like
    HTML entities etc.
    It is assumed tha the cleaner can be language-dependent.
    """
    rxTags = re.compile('</?(?:a|img|span|div|p|body|html|head)(?: [^<>]+)?>|[\0⌐-♯]+',
                        flags=re.DOTALL)
    rxSpaces1 = re.compile(' {2,}| +|\t+|&nbsp;| ', flags=re.DOTALL)
    rxSpaces2 = re.compile('(?: *\n)+ *', flags=re.DOTALL)
    rxPuncWords = re.compile('([,!?:;·;·)\\]>])([\\w(\\[<])')
    rxQuotesL = re.compile('([\\s(\\[{<\\-])"([\\w\\-\'`´‘’‛@.,-‒–—―•])',
                           flags=re.DOTALL)
    rxQuotesR = re.compile('([\\w\\-\'`´‘’‛/@.,-‒–—―•,!?:;·;·])"([\\s)\\]}>\\-.,!])',
                           flags=re.DOTALL)
    rxNonstandardQuotesL = re.compile('[“]', flags=re.DOTALL)
    rxNonstandardQuotesR = re.compile('[”]', flags=re.DOTALL)

    rxCyrISmall = re.compile('(?<=[Ѐ-ԧ])i|i(?=[Ѐ-ԧ])')
    rxCyrIBig = re.compile('(?<=[Ѐ-ԧ])I|I(?=[Ѐ-ԧ])')
    rxCyrAeSmall = re.compile('(?<=[Ѐ-ԧ])æ|æ(?=[Ѐ-ԧ])')
    rxCyrAeBig = re.compile('(?<=[Ѐ-ԧ])Æ|Æ(?=[Ѐ-ԧ])')
    rxCyrSchwaSmall = re.compile('(?<=[Ѐ-ԧ])[ǝə]|[ǝə](?=[Ѐ-ԧ])')
    rxCyrSchwaBig = re.compile('(?<=[Ѐ-ԧ])Ə|Ə(?=[Ѐ-ԧ])')
    rxCyrHSmall = re.compile('(?<=[Ѐ-ԧ])h|h(?=[Ѐ-ԧ])')
    rxCyrHBig = re.compile('(?<=[Ѐ-ԧ])H|H(?=[Ѐ-ԧ])')

    dictDiacriticsUdm = {'и': 'ӥ', 'о': 'ӧ', 'ж': 'ӝ',
                         'з': 'ӟ', 'ч': 'ӵ', 'И': 'Ӥ',
                         'О': 'Ӧ', 'Ж': 'Ӝ', 'З': 'Ӟ', 'Ч': 'Ӵ'}
    rxDiacriticsUdm = re.compile('([иожзчИОЖЗЧ])([:"])(?=[а-яА-ЯёЁ?!])')
    rxUdmU2I = re.compile('(?<=[а-яА-Я])[ћbü]')
    rxUdmO2O = re.compile('(?<=[а-яА-ЯӜӞӴӝӟӵ])[ќö]|[ќö](?=[а-яА-ЯӜӞӴӝӟӵ])')
    rxUdmX2Ch = re.compile('(?<=[а-яА-ЯӜӞӴӝӟӵ])[џx]|[џx](?=[а-яА-ЯӜӞӴӝӟӵ])')
    rxUdmDzh = re.compile('(?<=[а-яА-ЯӜӞӴӝӟӵ])љ|љ(?=[а-яА-ЯӜӞӴӝӟӵ])')
    rxUdmZj = re.compile('(?<=[а-яА-ЯӜӞӴӝӟӵ])њ|њ(?=[а-яА-ЯӜӞӴӝӟӵ])')

    rxArmPeriod = re.compile('(?<![a-zA-Z ]):')
    rxArmIntraWordPunc = re.compile('[՞՜՛]')
    rxArmOldCond = re.compile('^կը +')

    rxRNCStress = re.compile('`(\\w)')
    rxModifierStress = re.compile('(\\w)́')

    def __init__(self, lang):
        self.lang = lang

    def clean_text(self, text):
        """
        Main method that calls separate step-by-step procedures.
        """
        text = self.convert_html(text)
        text = self.clean_spaces(text)
        text = self.separate_words(text)
        text = self.clean_other(text)
        return text

    def convert_html(self, text):
        text = self.rxTags.sub('', text)  # deletes all tags in angle brackets
        text = html.unescape(text)
        return text

    def clean_spaces(self, text):
        text = self.rxSpaces1.sub(' ', text.strip())  # unify all spaces
        text = self.rxSpaces2.sub('\n ', text)  # normalize new lines
        return text

    def separate_words(self, text):
        # punctuation inside a word
        text = self.rxPuncWords.sub('\\1 \\2', text)  # adds a space between punctuation and next letter
        return text

    def convert_quotes(self, text):
        text = self.rxQuotesL.sub('\\1«\\2', text)
        text = self.rxQuotesR.sub('\\1»\\2', text)
        text = self.rxNonstandardQuotesL.sub(self.settings['left_quot_mark'], text)
        text = self.rxNonstandardQuotesR.sub(self.settings['right_quot_mark'], text)
        return text

    def clean_other(self, text):
        if self.lang == 'udm':
            text = text.replace('ü', 'ӥ')
        if self.lang in ['ukr', 'kaz', 'kpv', 'koi', 'kom']:
            text = self.rxCyrISmall.sub('і', text)
            text = self.rxCyrIBig.sub('І', text)
        if self.lang in ['kaz', 'tat', 'bak', 'xal']:
            text = self.rxCyrHSmall.sub('һ', text)
            text = self.rxCyrHBig.sub('Һ', text)
        if self.lang in ['kaz', 'tat', 'bak']:
            text = self.rxCyrSchwaSmall.sub('ә', text)
            text = self.rxCyrSchwaBig.sub('Ә', text)
        if self.lang in ['oss']:
            text = self.rxCyrAeSmall.sub('ӕ', text)
            text = self.rxCyrAeBig.sub('Ӕ', text)
        if self.lang in ['hye']:
            text = self.rxArmPeriod.sub('։', text)
        text = text.replace('…', '...')
        text = text.replace('\\r\\n', '\n')
        text = text.replace('\\n', '\n')
        text = text.replace('\\', '/')
        return text

    def clean_social_networks(self, text):
        text = re.sub('(?<=\\w)ааа+', 'а', text)
        text = re.sub('(?<=\\w)ооо+', 'о', text)
        text = re.sub('(?<=\\w)еее+', 'е', text)
        text = re.sub('(?<=\\w)ууу+', 'у', text)
        text = re.sub('(?<=\\w)иии+', 'у', text)
        text = re.sub('(?<=\\w)ыы+', 'ы', text)
        text = re.sub('(?<=\\w)ээ+', 'э', text)
        if self.lang in ['udm', 'kpv', 'koi', 'kom']:
            text = self.rxDiacriticsUdm.sub(lambda m: self.dictDiacriticsUdm[m.group(1)], text)
            text = self.rxUdmU2I.sub('ӥ', text)
            text = self.rxUdmO2O.sub('ӧ', text)
            text = self.rxUdmX2Ch.sub('ӵ', text)
            text = self.rxUdmDzh.sub('ӝ', text)
            text = self.rxUdmZj.sub('ӟ', text)
            text = re.sub('(?<=\\w)ӧӧ+', 'ӧ', text)
            text = re.sub('(?<=\\w)ӥӥ+', 'ӥ', text)
        return text

    def clean_token(self, text):
        """
        Clean a token for search purposes (the baseline will
        still have the original, uncleaned version).
        """
        wordClean = text
        if self.lang in ['hye']:
            wordClean = self.rxArmOldCond.sub('կ', text)
            wordClean = self.rxArmIntraWordPunc.sub('', wordClean)
        return wordClean
