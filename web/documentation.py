import mistune

class MathRenderer(mistune.HTMLRenderer):

    def codespan(self, text):
        return '`' + mistune.escape(text) + '`'



class Documentation():
    def __init__(self) -> None:
        self.markdown_documentation = {}
        self.markdown = mistune.create_markdown(
            renderer=MathRenderer(),
            hard_wrap=True,
        )

    def add(self, name: str, md: str) -> None:
        self.markdown_documentation[name] = md

    def get(self):
        return {
            key: self.markdown(md)
            for key, md in self.markdown_documentation.items()
        }
