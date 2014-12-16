"""
Created on Dec 8, 2014
Ahmed Maged : amaged@gmail.com
"""


from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug import secure_filename
import importlib
import os


app = Flask(__name__)

SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'scripts'))

def is_valid_rule(filename):
    return filename.lower().endswith('.py') and '__init__.py' != filename

@app.route('/')
def index():

    rules = []
    for filename in os.listdir(SCRIPTS_DIR):
        fullpath = os.path.join(SCRIPTS_DIR, filename)
        if(os.path.isfile(fullpath) and is_valid_rule(filename)):
            module_name = filename[:-3]

            python_module = importlib.import_module('scripts.%s' % module_name)
            description = python_module.description()

            rules += [(
                       filename,
                       module_name,
                       description
                       )]
            rules.sort()
    return render_template('index.html', rules=rules)

@app.route('/analyze', methods=['POST'])
def analyze():

    print request.method

    if request.method == 'POST':
        rules = request.form.getlist('rules')

        bug_id = request.form['bug_id']

        results = []
        for rule in rules:
            python_module = importlib.import_module('scripts.%s' % rule)
            message, value = python_module.analyze(bug_id)
            results += [(message, value)]
#             results += [(str(python_module), rule)]
#             results += [(rule, 1)]

        print results
        print bug_id

        return render_template('analysis_result.html', results=results, bug_id=bug_id)

    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['new_rule']

        print file.filename

        if file and is_valid_rule(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(SCRIPTS_DIR, filename))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5001)
