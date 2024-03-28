"""
1. open user videos
2. scroll down to load all videos
3. open firefox dev tools (ctrl+shift+k) or 
    right click on last video and select inspect
4. from the "Inspector" tab of the dev tools copy the HTML to local file:
    scroll up
    collapse <body> tag
    right click on it 
    copy
    outer HTML
5. Run script that will parse the HTML and will print the video titles
"""
from html.parser import HTMLParser

FILE_NAME = '/home/zhulien/work/data/youtube/get_titles_from_tiles_TEST'


class BananaParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.extracted = []

    def handle_starttag(self, tag, attrs):
        """
        Example: (with formatting for readability)
        tag: a, 
        attrs: [
            ('id', 'video-title-link'), 
            ('class', 'focus-on-expand ....'), 
            ('title', 'XXX_GET_THIS_XXX')
        ]
        """
        if tag != 'a' or not attrs:
            return

        id_match = False
        class_match = False
        title_value = None
        for t in attrs:
            attr_type = t[0]
            attr_value = t[1]
            if attr_type == 'id' and attr_value == 'video-title-link':
                id_match = True
            elif attr_type == 'class' and 'focus-on-expand' in attr_value:
                class_match = True
            elif attr_type == 'title':
                title_value = attr_value

        if id_match and class_match and title_value:
            self.extracted.append(title_value)

        # print('Start tag: %s, attrs: %s' % (tag, attrs))

    # def handle_endtag(self, tag):
    #     print('End tag: %s' % tag)
    #
    # def handle_data(self, data):
    #     print('Data: %s' % data)
    def print_extracted(self):
        print('Extracted %s:\n%s' %
              (len(self.extracted), '\n'.join(self.extracted)))

    def reset(self):
        super().reset()
        self.extracted = []

def read_html_from_file(file_name):
    print('Reading from file: %s' % file_name)
    with open(file_name) as fin:
        return fin.read()

def run():
    html_payload = read_html_from_file(FILE_NAME)
    parser = BananaParser()
    parser.feed(html_payload)
    parser.print_extracted()


if __name__ == '__main__':
    run()
