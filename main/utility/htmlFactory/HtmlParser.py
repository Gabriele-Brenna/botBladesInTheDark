from html import escape
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    """
    This class inherit from HTMLParser, and it is used to proper indent the html file.
    """
    def __init__(self):
        super().__init__()
        self.__t = 0
        self.lines = []
        self.__current_line = ''
        self.__current_tag = ''
        self.__current_tag_attrs = None

    @staticmethod
    def __attr_str(attrs):
        return ' '.join('{}="{}"'.format(name, escape(value)) for (name, value) in attrs)

    def handle_starttag(self, tag, attrs):
        """
        Method used to handle the starting tag of a html tag.

        :param tag: is the tag itself
        :param attrs: represent the attributes of the tag
        :return: None
        """
        if tag == 'b' or tag == 'span' or tag == 'i':
            self.__current_line += '<{}>'.format(tag + (' ' + self.__attr_str(attrs) if attrs else ''))
            return

        if tag != self.__current_tag or attrs != self.__current_tag_attrs:
            self.lines += [self.__current_line]

        self.__current_line = '\t' * self.__t + '<{}>'.format(tag + (' ' + self.__attr_str(attrs) if attrs else ''))

        self.__current_tag = tag
        self.__current_tag_attrs = attrs
        self.__t += 1

    def handle_endtag(self, tag):
        """
        Method used to handle the ending tag of a html tag.

        :param tag: is the tag itself
        :return: None
        """
        if tag == 'b' or tag == 'span' or tag == 'i':
            self.__current_line += '</{}>'.format(tag)
            return
        self.__t -= 1
        if tag != self.__current_tag:
            self.lines += [self.__current_line]
            self.lines += ['\t' * self.__t + '</{}>'.format(tag)]
        else:
            self.lines += [self.__current_line + '</{}>'.format(tag)]

        self.__current_line = ''

    def handle_startendtag(self, tag, attrs):
        """
        Method used to handle tag with no content.

        :param tag: is the tag itself
        :param attrs: represent the attributes of the tag
        :return: None
        """
        if tag == 'br':
            self.__current_line += '<{}/>'.format(tag + (' ' + self.__attr_str(attrs) if attrs else ''))
            self.__current_tag = tag
            return
        if tag != self.__current_tag:
            self.lines += [self.__current_line]

        self.__current_line = '\t' * self.__t + '<{}/>'.format(tag + (' ' + self.__attr_str(attrs) if attrs else ''))
        self.__current_tag = tag

    def handle_data(self, data):
        """
        Method used to handle the content of a html tag.

        :param data: content of the tag
        :return: None
        """
        self.__current_line += data

    def handle_decl(self, decl: str):
        """
        Method used to handle a declaration of a html document.

        :param decl: type of declaration
        :return: None
        """
        self.__current_line = '<!{}>'.format(decl)

    def get_parsed_string(self):
        """
        Method used to get a formatted string of the html document.

        :return: the formatted string
        """
        self.lines[0] = self.lines[0][:len(self.lines[0])-1]
        return '\n'.join(l for l in self.lines if l)
