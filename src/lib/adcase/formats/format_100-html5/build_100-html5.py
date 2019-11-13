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


def build(req):
  """Builder for this format.

  Args:
    req: flask request

  Returns:
    Json containing the creative data
  """
  errors = []
  v = {}
  if "zfile1" not in req.files:
    errors.append("No zip file")
    return {"errors": errors}

  zfile = req.files["zfile1"]
  ext = f.strtoken(zfile.filename.lower(),-1,".")

  if ext in ["jpg", "png", "gif"]:
    index = """<!DOCTYPE HTML><html lang="en-us">
<head>
  <meta name="ad.size" content="width=[[width]],height=[[height]]">
<script>
  var clickTag = "[[clicktag_url]]";
</script>
</head>
<body style='margin:0'>
  [[clicktag_layer]]
  <img src='image."""+ext+"""' style='border:0;width:[[width]];height:[[height]]'>

  <script>
    window.top.postMessage({ msg: "adcase", format:"html5", params: { action: "" } } , "*");
  </script>

</body></html>
"""
    tdir = "/tmp/" + f.get_tmp_file_name()
    f.mk_dir(tdir)
    zfile.save(tdir+'/image.'+ext)
    zfile.close()

    return {"errors": errors, "dir": tdir, "index": index, "vars": v}




  # unzip to temp dir
  tdir = "/tmp/" + f.get_tmp_file_name()

  if not f.extract_zip(zfile, tdir):
    return {"errors": ["No zip file"]}

  # get index content
  index = f.file_get_contents(tdir + "/index.html")
  if not index:
    errors.append("No index.html in zip file")

  # update head and body
  head = ("<head><meta name=\"ad.size\" content=\"width=[[width]],"
          "height=[[height]]\">")
  body = ("[[clicktag_layer]]<script>var clickTag = '[[clicktag_url]]';</scri"
          "pt><script data-exports-type='dclk-quick-preview'>if(typeof studio"
          " !== 'undefined' && studio.Enabler) { studio.Enabler.setRushSimula"
          "tedLocalEvents(true); }</script></body>")

  if index.find("<head>") < 0:
    errors.append("No <head> tag")
  if index.find("</body>") < 0:
    errors.append("No </body> tag")

  index = index.replace("<meta name=\"ad.size\"", "<meta name=\"old.adsize\"")
  index = index.replace("<head>", head)
  index = index.replace("</body>", body)
  index = index.replace("<meta name=\"GCD\"", "<meta name=\"old.GCD\"")

  return {"errors": errors, "dir": tdir, "index": index, "vars": v}
