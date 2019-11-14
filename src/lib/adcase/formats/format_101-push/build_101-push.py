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
"""Executes a build process for a 101-push format.
"""
import os
from lib.adcase import helper as f
import requests


# pylint: disable=line-too-long
def build(req):
  """Builder for this format.

  Args:
    req: flask request

  Returns:
    Json containing the creative data
  """
  current_path = os.path.dirname(__file__)

  errors = []
  v = {}
  dcm = (f.get_int_param("dcm") == 1)
  data = {"collapsed": {}, "expanded": {}}
  tdir = "/tmp/" + f.get_tmp_file_name()

  path = current_path + "/index_101-push.html"
  index = f.file_get_contents(path)

  if "collapsed_zip" not in req.files:
    return {"errors": ["No collapsed file"]}
  if "expanded_zip" not in req.files:
    return {"errors": ["No expanded file"]}

  ## collapsed
  data["collapsed"]["ext"] = f.get_ext(req.files["collapsed_zip"].filename)
  if data["collapsed"]["ext"] == "zip":
    os.mkdir(tdir)
    if not f.extract_zip(req.files["collapsed_zip"], tdir + "/collapsed"):
      return {"errors": ["Wrong collapsed zip file"]}

    file_name = "index2.js" if dcm else "index2.html"
    try:
      os.rename(tdir + "/collapsed/index.html", tdir+"/collapsed/" + file_name)
    except os.FileNotFoundError:
      return {"errors": ["No index.html in collapsed zip"]}

    if dcm:
      change_base(tdir+"/collapsed/" + file_name, "collapsed")
  elif not data["collapsed"]["ext"]:
    return {"errors": ["No collapsed file"]}
  else: 
    f.mk_dir(tdir)
    zfile = req.files["collapsed_zip"]
    zfile.save(tdir+'/collapsed.'+data["collapsed"]["ext"])
    zfile.close()

  ## expanded
  data["expanded"]["ext"] = f.get_ext(req.files["expanded_zip"].filename)
  if data["expanded"]["ext"] == "zip":
    if not f.extract_zip(req.files["expanded_zip"], tdir + "/expanded"):
      return {"errors": ["Wrong expanded zip file"]}

    file_name = "index2.js" if dcm else "index2.html"
    try:
      os.rename(tdir + "/expanded/index.html", tdir + "/expanded/" + file_name)
    except os.FileNotFoundError:
      return {"errors": ["No index.html in expanded zip"]}

    if dcm:
      change_base(tdir+"/expanded/" + file_name, "expanded")

  elif not data["expanded"]["ext"]:
    return {"errors": ["No expanded file"]}
  else: 
    f.mk_dir(tdir)
    zfile = req.files["expanded_zip"]
    zfile.save(tdir+'/expanded.'+data["expanded"]["ext"])
    zfile.close()

  v["initExpanded"] = "true" if f.get_param("initial_state") == "E" else "false"
  if f.get_param("initial_state") == "E":
    v["autocloseSeconds"] = f.get_param("autoclose_seconds")
  else:
    v["autocloseSeconds"] = "0"
  v["width"] = f.get_param("width")
  v["height"] = f.get_param("expanded_height")

  v["collapsedHeight"] = f.get_param("collapsed_height")
  v["expandedHeight"] = f.get_param("expanded_height")
  v["transitionTimeMs"] = str(f.get_int_param("animated_transition") * 250)
  v["expandAction"] = f.get_param("expand_action")
  v["collapseSeconds"] = f.get_param("collapse_seconds")

  if data["collapsed"]["ext"] == "zip":
    if dcm:
      v["collapsedContent"] = "<iframe id='iframe_collapsed' src='' frameborder=0 style='width:"+v["width"]+"px;height:"+v["collapsedHeight"]+"}px' scrolling='no'></iframe>"
    else:
      v["collapsedContent"] = "<iframe id='iframe_collapsed' src='collapsed/index2.html' frameborder=0 style='width:"+v["width"]+"px;height:"+v["collapsedHeight"]+"px' scrolling='no'></iframe>"
  else:
    v["collapsedContent"] = "<img src='collapsed."+data["collapsed"]["ext"]+"' style='border:0;width:"+v["width"]+"px;height:"+v["collapsedHeight"]+"px' />"

  if data["expanded"]["ext"] == "zip":
    if dcm:
      v["expandedContent"] = "<iframe id='iframe_expanded' src='' frameborder=0 style='width:"+v["width"]+"px;height:"+v["expandedHeight"]+"px' scrolling='no'></iframe>"
    else:
      v["expandedContent"] = "<iframe id='iframe_expanded' src='expanded/index2.html' frameborder=0 style='width:"+v["width"]+"px;height:"+v["expandedHeight"]+"px' scrolling='no'></iframe>"
  else:
    v["expandedContent"] = "<img src='expanded."+data["expanded"]["ext"]+"' style='border:0;width:"+v["width"]+"px;height:"+v["expandedHeight"]+"px' />"

  v["dcmScript"] = ""
  if dcm:
    if data["collapsed"]["ext"] == "zip":
      v["dcmScript"] = v["dcmScript"] + "\ndcm_load('collapsed');"
    if data["expanded"]["ext"] == "zip":
      v["dcmScript"] = v["dcmScript"] + "\ndcm_load('expanded');"

  return {"errors": errors, "dir": tdir, "index": index, "vars": v}

def change_base(file_path, new_folder):
  index = f.file_get_contents(file_path)
  index = index.replace("<head>", "<head><base href='"+new_folder+"'>")  
  f.file_put_contents(file_path, index)
 