import mistune


class MathRenderer(mistune.HTMLRenderer):

    def codespan(self, text):
        return '`' + mistune.escape(text) + '`'


render = mistune.create_markdown(
    renderer=MathRenderer(),
    hard_wrap=True,
)
