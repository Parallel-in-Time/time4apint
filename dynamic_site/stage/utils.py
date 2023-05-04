from unicodedata import normalize

import mistune


class MathRenderer(mistune.HTMLRenderer):

    def codespan(self, text):
        return '`' + mistune.escape(text) + '`'


render_md = mistune.create_markdown(
    renderer=MathRenderer(),
    hard_wrap=True,
)


def slugify(text: str):
    clean_text = text.strip().replace(' ', '-').lower()
    while '--' in clean_text:
        clean_text = clean_text.replace('--', '-')
    ascii_text = normalize('NFKD', clean_text).encode('ascii', 'ignore')
    strict_text = map(
        (lambda x: chr(x)
         if x in b'abcdefghijklmnopqrstuvwxyz0123456789-' else ''), ascii_text)
    return ''.join(strict_text)
