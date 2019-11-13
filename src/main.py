# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Application entry point."""
import os
import sys
from flask import Flask
from flask import redirect
from flask import request
from lib.adcase import build
from lib.adcase import builder
from lib.adcase import db
#from lib.adcase import demo
from lib.adcase import login
from lib.adcase import sizes

app = Flask(__name__)
app.debug = True

@app.before_request
def before_request():
  db.open_connection()


@app.route("/")
def home():
  """Default redirect.

  Returns:
    Redirect url.
  """
  return redirect("/builder/100-html5", code=302)


@app.route("/tmp")
def dirs_tmp():
  out = ""
  for root, directories, filenames in os.walk("/tmp/"):
    for directory in directories:
      out += "\n" + os.path.join(root, directory)
    for filename in filenames:
      out += "\n" + os.path.join(root, filename)
  return out


@app.route("/builder/<fmt>", methods=["GET"])
def main_builder(fmt):
  """Get builder form, depending on format.

  Returns:
    Json containing an html

  Args:
    fmt: format name to return. i.e. "html5"
  """
  print("FMT", fmt)
  out = builder.run(fmt)
  return out


@app.route("/builder/build/<fmt>", methods=["POST"])
def main_build(fmt):
  """Get builder form, depending on format.

  Returns:
    Json containing an html

  Args:
    fmt: format name to return. i.e. "html5"
  """
  sys.path.insert(0, "formats/" + fmt)
  out = build.run(fmt, request)
  return out


@app.route("/builder/sizes", methods=["GET", "POST"])
def main_sizes():
  """App api entry point.

  Returns:
    Json data
  """
  out = sizes.run(request)
  return out


@app.route("/builder/login/<action>", methods=["GET", "POST"])
def main_login(action):
  """App api entry point.

  Returns:
    Json data

  Args:
    action: action to execute.
  """
  out = login.run(request, action)
  return out


@app.route("/builder/demo", methods=["GET"])
def main_demo():
  """App api entry point.

  Returns:
    Json data
  """
  out = demo.run(request)
  return out
