from django.template.backends.jinja2 import Jinja2
from snaql.factory import RawFileSystemLoader, JinjaSQLExtension, Snaql as snaql_factory
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
        self.snaql = snaql_factory(None, self.env)

    def get_template(self, template_name):
        return self.snaql.load_queries(template_name)
