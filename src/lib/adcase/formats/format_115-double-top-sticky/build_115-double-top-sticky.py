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
  data = {"inline": {}, "sticky": {}}
  tdir = "/tmp/" + f.get_tmp_file_name()

  index = get_html()

  if "inline_zip" not in req.files:
    return {"errors": ["No inline file"]}
  if "sticky_zip" not in req.files:
    return {"errors": ["No sticky file"]}

  ## inline
  data["inline"]["ext"] = f.get_ext(req.files["inline_zip"].filename)
  if data["inline"]["ext"] == "zip":
    os.mkdir(tdir)
    if not f.extract_zip(req.files["inline_zip"], tdir + "/inline"):
      return {"errors": ["Wrong inline zip file"]}

    file_name = "index2.html"
    try:
      os.rename(tdir + "/inline/index.html", tdir + "/inline/" + file_name)
    except os.FileNotFoundError:
      return {"errors": ["No index.html in inline zip"]}
  elif not data["inline"]["ext"]:
    return {"errors": ["No inline file"]}
  else:
    f.save_file(req.files["inline_zip"], tdir + "/inline." + data["inline"]["ext"])

  ## sticky
  data["sticky"]["ext"] = f.get_ext(req.files["sticky_zip"].filename)
  if data["sticky"]["ext"] == "zip":
    if not f.extract_zip(req.files["sticky_zip"], tdir + "/sticky"):
      return {"errors": ["Wrong sticky zip file"]}

    file_name = "index2.html"
    try:
      os.rename(tdir + "/sticky/index.html", tdir + "/sticky/" + file_name)
    except os.FileNotFoundError:
      return {"errors": ["No index.html in sticky zip"]}
  elif not data["sticky"]["ext"]:
    return {"errors": ["No sticky file"]}
  else:
    f.save_file(req.files["sticky_zip"], tdir + "/sticky." + data["sticky"]["ext"])

  v["width"] = f.get_param("width")

  v["inlineHeight"] = f.get_int_param("inline_height")
  v["stickyHeight"] = f.get_int_param("sticky_height")
  v["maxHeight"] = str(max(v["inlineHeight"], v["stickyHeight"]))
  v["height"] = v["maxHeight"]
  v["transitionTimeMs"] = str(f.get_int_param("animated_transition") * 250)

  v["inlinePosition"] = f.get_param("inline_position")
  v["inlinePositionDivId"] = f.get_param("inline_position_div_id")
  v["topMargin"] = f.get_param("top_margin")

  if data["inline"]["ext"] == "zip":
    v["inlineContent"] = "<iframe src='inline/index2.html' frameborder=0 style='width:"+v["width"]+"px;height:"+str(v["inlineHeight"])+"px' scrolling='no'></iframe>"
  else:
    v["inlineContent"] = "<img src='inline."+data["inline"]["ext"]+"' style='border:0;width:"+v["width"]+"px;height:"+str(v["inlineHeight"])+"px' />"

  if data["sticky"]["ext"] == "zip":
    v["stickyContent"] = "<iframe src='sticky/index2.html' frameborder=0 style='width:"+v["width"]+"px;height:"+str(v["stickyHeight"])+"px' scrolling='no'></iframe>"
  else:
    v["stickyContent"] = "<img src='sticky."+data["sticky"]["ext"]+"' style='border:0;width:"+v["width"]+"px;height:"+str(v["stickyHeight"])+"px' />"

  return {"errors": errors, "dir": tdir, "index": index, "vars": v}


def get_html():
  """Gets html.

  Returns:
    index.html content
  """

  return """<!DOCTYPE HTML><html lang="en-us">
<head>
  <meta name="ad.size" content="width=[[width]],height=[[maxHeight]]">
</head>
<body style='margin:0'>
[[clicktag_layer]]
  <div id='ad_inline' style='display:;width:[[width]]px;height:[[inlineHeight]]px;overflow:hidden;'>
    [[inlineContent]]
  </div>
  <div id='ad_sticky' style='display:none;width:[[width]]px;height:[[stickyHeight]]px;overflow:hidden;'>
    [[stickyContent]]
  </div>
<script>
  var clickTag = "[[clicktag_url]]";
  tpl = { };
  tpl.receiveMessages = function(e) {
    if(e.data && e.data.sticky && (e.data.sticky=="on" || e.data.sticky=="off")) {
      tpl.sync(e.data.sticky);
    }
  }

  window.addEventListener ? window.addEventListener("message", tpl.receiveMessages, !1)
    : (window.attachEvent && window.attachEvent("message", tpl.receiveMessages));

  tpl.sync = function(sticky) {
    document.getElementById("ad_inline") && (document.getElementById("ad_inline").style.display = (sticky=="on"?"none":"block"));
    document.getElementById("ad_sticky") && (document.getElementById("ad_sticky").style.display = (sticky=="off"?"none":"block"));
  }

window.top.postMessage({ msg: "adcase", format:"doubleTopSticky",
    params: { action: "doubleTopStickyLoaded", inlineHeight: [[inlineHeight]], stickyHeight: [[stickyHeight]]
    ,inlinePosition:"[[inlinePosition]]", inlinePositionDivId:"[[inlinePositionDivId]]", transition:[[transitionTimeMs]], width:[[width]], topMargin:[[topMargin]] } } , "*");

</script>
</body></html>"""
