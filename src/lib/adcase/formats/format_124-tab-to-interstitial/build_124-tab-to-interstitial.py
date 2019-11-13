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
import os
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
  data = {"tab": {}, "expanded": {}}
  tdir = "/tmp/" + f.get_tmp_file_name()

  index = get_html()

  if "tab_zip" not in req.files:
    return {"errors": ["No tab file"]}
  if "expanded_zip" not in req.files:
    return {"errors": ["No expanded file"]}

  ## tab
  data["tab"]["ext"] = f.get_ext(req.files["tab_zip"].filename)
  if data["tab"]["ext"] == "zip":
    os.mkdir(tdir)
    if not f.extract_zip(req.files["tab_zip"], tdir + "/tab"):
      return {"errors": ["Wrong tab zip file"]}

    file_name = "index2.html"
    try:
      os.rename(tdir + "/tab/index.html", tdir + "/tab/" + file_name)
    except os.FileNotFoundError:
      return {"errors": ["No index.html in tab zip"]}
  elif not data["tab"]["ext"]:
    return {"errors": ["No tab file"]}
  else:
    f.save_file(req.files["tab_zip"], tdir + "/tab." + data["tab"]["ext"])

  ## expanded
  data["expanded"]["ext"] = f.get_ext(req.files["expanded_zip"].filename)
  if data["expanded"]["ext"] == "zip":
    if not f.extract_zip(req.files["expanded_zip"], tdir + "/expanded"):
      return {"errors": ["Wrong expanded zip file"]}

    file_name = "index2.html"
    try:
      os.rename(tdir + "/expanded/index.html", tdir + "/expanded/" + file_name)
    except os.FileNotFoundError:
      return {"errors": ["No index.html in expanded zip"]}
  elif not data["expanded"]["ext"]:
    return {"errors": ["No expanded file"]}
  else:
    f.save_file(req.files["expanded_zip"], tdir + "/expanded." + data["expanded"]["ext"])

  v["expandMS"] = str(f.get_int_param("expand_seconds") * 1000)

  v["width"] = f.strtoken(f.get_param("size"), 1, "x")
  v["height"] = f.strtoken(f.get_param("size"), 2, "x")

  v["backgroundColor"] = f.get_param("background_color")

  v["clicktag_layer_select"] = "true" if f.get_param("clicktag_layer") else "false"

  v["tabURL"] = ""
  v["tabImage"] = ""

  if data["tab"]["ext"] == "zip":
    v["tabUrl"] = "tab/index2.html"
  else:
    v["tabImage"] = "tab."+data["tab"]["ext"]

  v["expandedURL"] = ""
  v["expandedImage"] = ""
  if data["expanded"]["ext"] == "zip":
    v["expandedURL"] = "expanded/index2.html"
  else:
    v["expandedImage"] = "expanded."+data["expanded"]["ext"]

  return {"errors": errors, "dir": tdir, "index": index, "vars": v}


def get_html():
  """Index.html content.

  Returns:
    index.html content
  """

  return """<!DOCTYPE HTML><html lang="en-us">
<head>
  <meta name="ad.size" content="width=[[width]],height=[[height]]">
<script>
var clickTag = "[[clicktag_url]]";
var ads = { };

ads.receiveMessage = function(e) {
  e.data = e.data || {};
  if(e.data.msg && e.data.action) {
    if(e.data.msg == "adcase" && e.data.action == "click") {
      window.top.postMessage({ msg: 'adcase_click', format:'tab-to-interstitial' }, '*'); 
      window.open(clickTag, '_blank');
    }
  }
}

window.addEventListener ? window.addEventListener("message", ads.receiveMessage, !1)
: (window.attachEvent && window.attachEvent("message", ads.receiveMessage));
</script>
</head>
<body style='margin:0;cursor:pointer'>
[[clicktag_layer]]
<script>
    window.top.postMessage({ msg:"adcase", format:124, version:4, params:{ittHeight:"[[height]]",ittWidth:"[[width]]","ittType":"tab2ITT",
      urlPrefix: document.location.href.substring(0,document.location.href.length-10),
      expandedURL:"[[expandedURL]]",expandedImage:"[[expandedImage]]",
      tabURL:"[[tabURL]]",tabImage:"[[tabImage]]",
      tabClass:"tabsbanner",backgroundColor:"[[backgroundColor]]",
      clicktagLayer:[[clicktag_layer_select]], clicktagURL:"[[clicktag_url]]" }},"*");
</script>
</body></html>"""
