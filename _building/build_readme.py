#!/usr/bin/env python
# coding: utf-8

import os
import imp
import yaml
import jinja2

# xxx/_building/build_readme.py
this_base = os.path.dirname(__file__)

j2vars = {}

# load package name from __init__.py
pkg = imp.load_source("_foo", '__init__.py')
j2vars["name"] = pkg._name

def get_gh_config():
    with open('.github/settings.yml', 'r') as f:
        cont = f.read()

    cfg = yaml.safe_load(cont)
    tags = cfg['repository']['topics'].split(',')
    tags = [x.strip() for x in tags]
    cfg['repository']['topics'] = tags
    return cfg

cfg = get_gh_config()
j2vars['description'] = cfg['repository']['description']

def render_j2(tmpl_path, tmpl_vars, output_path):
    template_loader = jinja2.FileSystemLoader(searchpath='./')
    template_env = jinja2.Environment(loader=template_loader,
                                      undefined=jinja2.StrictUndefined)
    template = template_env.get_template(tmpl_path)

    txt = template.render(tmpl_vars)

    with open(output_path, 'w') as f:
        f.write(txt)

if __name__ == "__main__":
    render_j2('_building/README.md.j2',
       j2vars,
       'README.md')
