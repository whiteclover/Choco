import io
import os
import unittest
from .. import TemplateTest, template_base, skip_if
from choco import compat

try:
    import babel.messages.extract as babel
    from choco.ext.babelplugin import extract
    
except ImportError:
    babel = None


def skip():
    return skip_if(
        lambda: not babel,
        'babel not installed: skipping babelplugin test')


class Test_extract(unittest.TestCase):
    @skip()
    def test_parse_python_expression(self):
        input = io.BytesIO(compat.b('<p>${_("Message")}</p>'))
        messages = list(extract(input, ['_'], [], {}))
        self.assertEqual(messages, [(1, '_', compat.u('Message'), [])])

    @skip()
    def test_python_gettext_call(self):
        input = io.BytesIO(compat.b('<p>${_("Message")}</p>'))
        messages = list(extract(input, ['_'], [], {}))
        self.assertEqual(messages, [(1, '_', compat.u('Message'), [])])

    @skip()
    def test_translator_comment(self):
        input = io.BytesIO(compat.b('''
        <p>
          ## TRANSLATORS: This is a comment.
          ${_("Message")}
        </p>'''))
        messages = list(extract(input, ['_'], ['TRANSLATORS:'], {}))
        self.assertEqual(
            messages,
            [(4, '_', compat.u('Message'),
                [compat.u('TRANSLATORS: This is a comment.')])])


class ExtractChocoTestCase(TemplateTest):
    @skip()
    def test_extract(self):
        choco_tmpl = open(os.path.join(template_base, 'gettext.choco'))
        messages = list(extract(choco_tmpl, {'_': None, 'gettext': None,
                                            'ungettext': (1, 2)},
                                ['TRANSLATOR:'], {}))
        expected = \
            [(1, '_', 'Page arg 1', []),
             (1, '_', 'Page arg 2', []),
             (10, 'gettext', 'Begin', []),
             (14, '_', 'Hi there!', ['TRANSLATOR: Hi there!']),
             (19, '_', 'Hello', []),
             (22, '_', 'Welcome', []),
             (25, '_', 'Yo', []),
             (36, '_', 'The', ['TRANSLATOR: Ensure so and', 'so, thanks']),
             (36, 'ungettext', ('bunny', 'bunnies', None), []),
             (41, '_', 'Goodbye', ['TRANSLATOR: Good bye']),
             (44, '_', 'Babel', []),
             (45, 'ungettext', ('hella', 'hellas', None), []),
             (62, '_', 'The', ['TRANSLATOR: Ensure so and', 'so, thanks']),
             (62, 'ungettext', ('bunny', 'bunnies', None), []),
             (68, '_', 'Goodbye, really!', ['TRANSLATOR: HTML comment']),
             (71, '_', 'P.S. byebye', []),
             (77, '_', 'Top', []),
             (83, '_', 'foo', []),
             (83, '_', 'hoho', []),
             (85, '_', 'bar', []),
             (92, '_', 'Inside a p tag', ['TRANSLATOR: <p> tag is ok?']),
             (95, '_', 'Later in a p tag', ['TRANSLATOR: also this']),
             (99, '_', 'No action at a distance.', []),
             ]
        self.assertEqual(expected, messages)

    @skip()
    def test_extract_utf8(self):
        choco_tmpl = open(os.path.join(template_base, 'gettext_utf8.choco'), 'rb')
        message = next(extract(choco_tmpl, set(['_', None]), [], {'encoding': 'utf-8'}))
        assert message == (1, '_', u'K\xf6ln', [])

    @skip()
    def test_extract_cp1251(self):
        choco_tmpl = open(os.path.join(template_base, 'gettext_cp1251.choco'), 'rb')
        message = next(extract(choco_tmpl, set(['_', None]), [], {'encoding': 'cp1251'}))
        # "test" in Rusian. File encoding is cp1251 (aka "windows-1251")
        assert message == (1, '_', u'\u0442\u0435\u0441\u0442', [])
