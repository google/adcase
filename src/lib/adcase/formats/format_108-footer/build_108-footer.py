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

"""Executes a build process for a format.
"""
from lib.adcase import helper as f
# pylint: disable=line-too-long


def build(req):
  """Builder for this format.

  Args:
    req: flask request

  Returns:
    Json containing the creative data
  """
  errors = []
  v = {}
  tdir = "/tmp/" + f.get_tmp_file_name()

  if f.get_param("source") == "tag":
    # tag
    v["tag"] = f.get_param("tag")
    index = get_index_tag()
  else:
    # zip
    if "zipfile" not in req.files:
      return {"errors": ["No uploaded file"]}

    zfile = req.files["zipfile"]
    ext = f.get_ext(zfile.filename)
    if ext == "zip":
      if not f.extract_zip(zfile, tdir):
        return {"errors": ["Can't decompress zip file"]}

      index = f.file_get_contents(tdir + "/index.html")
      if not index:
        return {"errors": ["No index.html in Zip file"]}

      if index.find("<head>") < 0:
        return {"errors": ["No <head> tag in index.html"]}
      if index.find("</body>") < 0:
        return {"errors": ["No </body> tag in index.html"]}
    else:
      # image
      f.save_file(req.files["zipfile"], tdir + "/image." + ext)
      v["image_ext"] = ext
      index = get_index_image()

  v["autoclose"] = str(f.get_int_param("autoclose"))
  v["bgcolor"] = f.get_param("bgcolor")
  v["width"] = f.get_param("width")
  v["height"] = f.get_param("collapsed_height")

  index = replace_html(index)

  return {"errors": errors, "dir": tdir, "index": index, "vars": v}


def get_index_image():
  """Formats html.

  Returns:
    Modified index.html content
  """

  return """<!DOCTYPE HTML><html lang="en-us">
    <head>
    </head>
    <body style='margin:0'>
      <img src='image.[[image_ext]]'>
    </body>
    </html>"""


def get_index_tag():
  """Formats html.

  Returns:
    Modified index.html content
  """

  return """<!DOCTYPE HTML><html lang="en-us">
<head>
</head>
<body style='margin:0' >
[[tag]]
</body>
</html>"""


def replace_html(index):
  """Formats html.

  Args:
    index: index html content

  Returns:
    Modified index.html content
  """

  body = """  [[clicktag_layer]]
<script>
  var clickTag = "[[clicktag_url]]";
</script>
<script data-exports-type="dclk-quick-preview">if(typeof studio !== "undefined" && studio.Enabler) { studio.Enabler.setRushSimulatedLocalEvents(true); }
</script>
<script>
window.top.postMessage({ msg: "adcase", format:"footerFixed", params: { height: [[height]], type:"standard", action:"setup" }}, "*");
</script>
</body>"""

  head = "<head><meta name=\"ad.size\" content=\"width=[[width]],height=[[height]]\">"

  index = index.replace("<meta name=\"ad.size\"", "<meta name=\"old.adsize\"")
  index = index.replace("<head>", head)
  index = index.replace("</body>", body)
  index = index.replace("<meta name=\"GCD\"", "<meta name=\"old.GCD\"")

  return index
