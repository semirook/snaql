import sys
from copy import deepcopy

from django.template.backends.jinja2 import Jinja2
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.utils import six
from snaql.factory import RawFileSystemLoader, JinjaSQLExtension, Snaql as snaql_factory
import jinja2
from jinja2.environment import load_extensions


class Snaql(Jinja2):

    app_dirname = 'snaql'

    def __init__(self, params):
        params  = params.copy()
        options = params.pop('OPTIONS', {}).copy()
        options.setdefault('trim_blocks', True)
        params['OPTIONS'] = options
        super(Snaql, self).__init__(params)
        self.env.extensions.update(load_extensions(self.env, [JinjaSQLExtension]))
        self.env.loader = RawFileSystemLoader(self.template_dirs)

    def get_template(self, template_name):
        snaql = snaql_factory(None, deepcopy(self.env))
        try:
            return snaql.load_queries(template_name)
        except jinja2.TemplateNotFound as exc:
            six.reraise(TemplateDoesNotExist, TemplateDoesNotExist(exc.args),
                sys.exc_info()[2])
        except jinja2.TemplateSyntaxError as exc:
            six.reraise(TemplateSyntaxError, TemplateSyntaxError(exc.args),
                sys.exc_info()[2])
