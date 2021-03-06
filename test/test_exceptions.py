# -*- coding: utf-8 -*-
import sys

from choco import errors, compat
from choco.template import Template
from choco.lookup import TemplateLookup
from choco.compat import u
from test.util import result_lines
from test import TemplateTest
from test import requires_pygments_14, requires_no_pygments_errors

class ExceptionsTest(TemplateTest):
    def test_html_error_template(self):
        """test the html_error_template"""
        code = """
% i = 0
"""
        try:
            template = Template(code)
            template.render_unicode()
            assert False
        except errors.CompileException:
            html_error = errors.html_error_template().render_unicode()
            assert ("CompileException: Fragment &#39;i = 0&#39; is not "
                    "a partial control statement at line: 2 char: 1") in html_error
            assert '<style>' in html_error
            html_error_stripped = html_error.strip()
            assert html_error_stripped.startswith('<html>')
            assert html_error_stripped.endswith('</html>')

            not_full = errors.html_error_template().\
                                    render_unicode(full=False)
            assert '<html>' not in not_full
            assert '<style>' in not_full

            no_css = errors.html_error_template().\
                                    render_unicode(css=False)
            assert '<style>' not in no_css
        else:
            assert False, ("This function should trigger a CompileException, "
                           "but didn't")

    def test_text_error_template(self):
        code = """
% i = 0
"""
        try:
            template = Template(code)
            template.render_unicode()
            assert False
        except errors.CompileException:
            text_error = errors.text_error_template().render_unicode()
            assert 'Traceback (most recent call last):' in text_error
            assert ("CompileException: Fragment 'i = 0' is not a partial "
                    "control statement") in text_error

    @requires_pygments_14
    def test_utf8_html_error_template_pygments(self):
        """test the html_error_template with a Template containing UTF-8
        chars"""

        if compat.py3k:
            code = """# -*- coding: utf-8 -*-
% if 2 == 2: /an error
${'привет'}
% endif
"""
        else:
            code = """# -*- coding: utf-8 -*-
% if 2 == 2: /an error
${u'привет'}
% endif
"""
        try:
            template = Template(code)
            template.render_unicode()
        except errors.CompileException:
            html_error = errors.html_error_template().render()
            if compat.py3k:
                assert ("CompileException: Fragment &#39;if 2 == 2: /an "
                    "error&#39; is not a partial control statement "
                    "at line: 2 char: 1").encode(sys.getdefaultencoding(), 'htmlentityreplace') in \
                    html_error
            else:
                assert ("CompileException: Fragment &#39;if 2 == 2: /an "
                        "error&#39; is not a partial control statement "
                        "at line: 2 char: 1") in \
                        html_error

            if compat.py3k:
                assert "".encode(sys.getdefaultencoding(),
                                        'htmlentityreplace') in html_error
            else:
                assert 'u&#39;'\
                        '&#x43F;&#x440;&#x438;&#x432;&#x435;&#x442;'\
                        '&#39;</span><span class="cp">}</span>'.encode(
                                sys.getdefaultencoding(),
                                'htmlentityreplace') in html_error
        else:
            assert False, ("This function should trigger a CompileException, "
                           "but didn't")

    @requires_no_pygments_errors
    def test_utf8_html_error_template_no_pygments(self):
        """test the html_error_template with a Template containing UTF-8
        chars"""

        if compat.py3k:
            code = """# -*- coding: utf-8 -*-
% if 2 == 2: /an error
${'привет'}
% endif
"""
        else:
            code = """# -*- coding: utf-8 -*-
% if 2 == 2: /an error
${u'привет'}
% endif
"""
        try:
            template = Template(code)
            template.render_unicode()
        except errors.CompileException:
            html_error = errors.html_error_template().render()
            if compat.py3k:
                assert ("CompileException: Fragment &#39;if 2 == 2: /an "
                    "error&#39; is not a partial control statement "
                    "at line: 2 char: 1").encode(sys.getdefaultencoding(),
                            'htmlentityreplace') in \
                    html_error
            else:
                assert ("CompileException: Fragment &#39;if 2 == 2: /an "
                        "error&#39; is not a partial control statement "
                        "at line: 2 char: 1") in \
                        html_error

            if compat.py3k:
                assert "${&#39;привет&#39;}".encode(sys.getdefaultencoding(),
                                 'htmlentityreplace') in html_error
            else:
                assert u("${u&#39;привет&#39;}").encode(sys.getdefaultencoding(),
                                    'htmlentityreplace') in html_error
        else:
            assert False, ("This function should trigger a CompileException, "
                           "but didn't")

    def test_format_closures(self):
        try:
            exec("def foo():"\
                 "    raise RuntimeError('test')", locals())
            foo()
        except:
            html_error = errors.html_error_template().render()
            assert "RuntimeError: test" in str(html_error)

    def test_py_utf8_html_error_template(self):
        try:
            foo = u('日本')
            raise RuntimeError('test')
        except:
            html_error = errors.html_error_template().render()
            if compat.py3k:
                assert 'RuntimeError: test' in html_error.decode('utf-8')
                assert "foo = u(&#39;日本&#39;)" in html_error.decode('utf-8')
            else:
                assert 'RuntimeError: test' in html_error
                assert "foo = u(&#39;&#x65E5;&#x672C;&#39;)" in html_error

    def test_py_unicode_error_html_error_template(self):
        try:
            raise RuntimeError(u('日本'))
        except:
            html_error = errors.html_error_template().render()
            assert u("RuntimeError: 日本").encode('ascii', 'ignore') in html_error

    @requires_pygments_14
    def test_format_errors_pygments(self):
        l = TemplateLookup(format_errors=True)

        l.put_string("foo.html", """
<%inherit file="base.html"/>
${foobar}
        """)

        l.put_string("base.html", """
        ${self.body()}
        """)

        assert '<div class="sourceline"><table class="syntax-highlightedtable">' in \
            l.get_template("foo.html").render_unicode()

    @requires_no_pygments_errors
    def test_format_errors_no_pygments(self):
        l = TemplateLookup(format_errors=True)

        l.put_string("foo.html", """
<%inherit file="base.html"/>
${foobar}
        """)

        l.put_string("base.html", """
        ${self.body()}
        """)

        assert '<div class="sourceline">${foobar}</div>' in \
            result_lines(l.get_template("foo.html").render_unicode())

    @requires_pygments_14
    def test_utf8_format_errors_pygments(self):
        """test that htmlentityreplace formatting is applied to
           errors reported with format_errors=True"""

        l = TemplateLookup(format_errors=True)
        if compat.py3k:
            l.put_string("foo.html", """# -*- coding: utf-8 -*-\n${'привет' + foobar}""")
        else:
            l.put_string("foo.html", """# -*- coding: utf-8 -*-\n${u'привет' + foobar}""")

        if compat.py3k:
            assert '&#39;привет&#39;</span>' in \
                l.get_template("foo.html").render().decode('utf-8')
        else:
            assert 'u&#39;&#x43F;&#x440;&#x438;&#x432;'\
                    '&#x435;&#x442;&#39;</span>' in \
                l.get_template("foo.html").render().decode('utf-8')

    @requires_no_pygments_errors
    def test_utf8_format_errors_no_pygments(self):
        """test that htmlentityreplace formatting is applied to
           errors reported with format_errors=True"""

        l = TemplateLookup(format_errors=True)
        if compat.py3k:
            l.put_string("foo.html", """# -*- coding: utf-8 -*-\n${'привет' + foobar}""")
        else:
            l.put_string("foo.html", """# -*- coding: utf-8 -*-\n${u'привет' + foobar}""")

        if compat.py3k:
            assert '<div class="sourceline">${&#39;привет&#39; + foobar}</div>'\
                in result_lines(l.get_template("foo.html").render().decode('utf-8'))
        else:
            assert '${u&#39;&#x43F;&#x440;&#x438;&#x432;&#x435;'\
                   '&#x442;&#39; + foobar}' in \
                result_lines(l.get_template("foo.html").render().decode('utf-8'))


    def test_custom_tback(self):
        try:
            raise RuntimeError("error 1")
            foo('bar')
        except:
            t, v, tback = sys.exc_info()

        try:
            raise RuntimeError("error 2")
        except:
            html_error = errors.html_error_template().\
                        render_unicode(error=v, traceback=tback)

        # obfuscate the text so that this text
        # isn't in the 'wrong' exception
        assert "".join(reversed(");93#&rab;93#&(oof")) in html_error

    def test_tback_no_trace_from_py_file(self):
        try:
            t = self._file_template("runtimeerr.html")
            t.render()
        except:
            t, v, tback = sys.exc_info()

        if not compat.py3k:
            # blow away tracebaack info
            sys.exc_clear()

        # and don't even send what we have.
        html_error = errors.html_error_template().\
                    render_unicode(error=v, traceback=None)
        assert "local variable &#39;y&#39; referenced before assignment" in html_error

    def test_tback_trace_from_py_file(self):
        t = self._file_template("runtimeerr.html")
        try:
            t.render()
            assert False
        except:
            html_error = errors.html_error_template().\
                        render_unicode()

        assert "local variable &#39;y&#39; referenced before assignment" in html_error
