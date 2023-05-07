import importlib
import os
import pkgutil
import glob
from inspect import getmembers, isclass

from flask import Flask, jsonify, render_template, abort, request

import dynamic_site
from dynamic_site.app import App

import mistune
from mistune.directives import Image, Figure, FencedDirective


def import_module(path):
    package = importlib.import_module(path)
    results = {}
    for _, name, _ in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
    return results


class Site:

    def __init__(self,
                 apps_path: str = 'web_apps',
                 escape_html_in_md: bool = True) -> None:
        self.apps_path = apps_path
        self.dynamic_site_path = os.path.dirname(dynamic_site.__file__)
        self.render_md = mistune.create_markdown(
            plugins=[
                'math',
                'table',
                'footnotes',
                'strikethrough',
                FencedDirective([
                    Image(),
                    Figure(),
                ]),
            ],
            escape=escape_html_in_md,
        )

        self.generate_apps()

        self.index_file = f'{apps_path}/index.md'
        if not os.path.exists(self.index_file):
            raise RuntimeError(f'There is no index.md file in "{apps_path}"!')

        self.initialize_flask_server()

    def generate_apps(self) -> None:
        modules = import_module(self.apps_path)
        self.apps = {}
        for name, module in modules.items():
            apps = [
                a for a in getmembers(module)
                # If its a class, then check if its a subclass, but not the actual App-Class
                if isclass(a[1]) and issubclass(a[1], App) and a[1] != App
            ]
            if len(apps) == 1:
                module_name = name.split('.')[1]  # Remove the web_apps.
                self.apps[module_name] = apps[0][1]()  # Create an instance
            elif len(apps) > 1:
                raise RuntimeError(
                    f'In {name} are multiple apps defined! Only define one!')
        print(f'Found apps: {list(self.apps.keys())}')

    def initialize_flask_server(self) -> None:
        STATIC_FOLDER = f'{self.dynamic_site_path}/static'
        self.flask_app = Flask(
            __name__,
            static_url_path='',
            static_folder=STATIC_FOLDER,
            template_folder=f'{self.dynamic_site_path}/templates')

        @self.flask_app.route('/')
        def index():
            text = self.render_md(open(self.index_file).read())
            return render_template('index.html', text=text)

        @self.flask_app.route('/<app_name>')
        def app_route(app_name):
            # If the app_name doesn't exist raise a 404
            if app_name not in self.apps.keys():
                abort(404)

            # Fetch the documentation which should have the same name as the app
            documentation = ''
            if os.path.exists(f'{self.apps_path}/{app_name}.md'):
                documentation = self.render_md(
                    open(f'{self.apps_path}/{app_name}.md').read())

            # Get the app title (raises an error if empty)
            app_title = self.apps[app_name].title

            # Then render the template and inject the corresponding documentation
            return render_template('app.html',
                                   title=app_title,
                                   documentation=documentation)

        @self.flask_app.route('/<app_name>/compute', methods=['POST'])
        def app_compute(app_name):
            # If the app_name doesn't exist raise a 404
            if app_name not in self.apps.keys():
                abort(404)

            # Otherwise get the correct app
            request_json = request.json
            request_data = None if not request_json else request_json
            docs, settings, plots = self.apps[app_name].compute(
                request_data).get_stages()

            # Serialize them to objects
            docs = [stage.serialize() for stage in docs]
            settings = [stage.serialize() for stage in settings]
            plots = [stage.serialize() for stage in plots]
            return jsonify({
                'docs': docs,
                'settings': settings,
                'plots': plots
            })

    def run(self) -> None:
        self.flask_app.run(debug=True, host="0.0.0.0", port=8000)
