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
"""Get builder form, depending on format."""
import importlib
import os
import sys
from flask import jsonify
from lib.adcase import db
from lib.adcase import helper as f


def run(fmt, req):
  """Builder entry point.

  Dinamycally loads builder module.

  Args:
    fmt: format to build
    req: flask request

  Returns:
    Json containing the creative url for download
  """
  format_id = fmt.split("-")[0]
  format_name = fmt[4:]

  user_id = f.get_user_id(req)
  if user_id is None:
    return jsonify({"errors": ["Please login before running build process"]})

  # get creative id: formatId.userId.creativeId.zip
  new_id = db.res(
      "select ifnull(max(file_id)+1,1) id "
      "from   creatives "
      "where  user_id = %s "
      "and    format = %s", (user_id, format_id))

  ## load builder dinamically

  # run builder
  current_path = os.path.dirname(__file__)

  sys.path.append(current_path + "/formats/format_" + fmt)
  module1 = importlib.import_module("build_" + fmt)
  build = module1.build(req)

  if has_errors(build):
    return jsonify({"errors": build["errors"]})

  index = build["index"]

  ## replace standard vars
  v = {}
  if "vars" in build:
    v = build["vars"]

  v["autoclose"] = f.get_param("autoclose")
  v["close_button"] = f.get_param("close_button")
  v["close_button_width"] = f.get_param("close_button_width")
  v["close_button_height"] = f.get_param("close_button_height")
  v["bgcolor"] = f.get_param("bgcolor")

  import re
  if "width" in v:
    v["width"] = re.sub("\D", "", v["width"])
  if "height" in v:
    v["height"] = re.sub("\D", "", v["height"])

  if "width" not in v:
    if f.get_param("size"):
      v["width"] = f.get_param("size").split("x")[0]
    else:
      v["width"] = ""

  if "height" not in v:
    if f.get_param("size") and len(f.get_param("size").split("x")):
      v["height"] = f.get_param("size").split("x")[1]
    else:
      v["height"] = ""

  # clicktag_url
  clicktag_url = f.get_param("clicktag_url")
  if clicktag_url.lower()[0:4] != "http":
    clicktag_url = "http://" + clicktag_url
  v["clicktag_url"] = clicktag_url

  # clicktag_layer
  if f.get_param("clicktag_layer"):
    v["clicktag_layer"] = (
        "<div style = 'position: fixed; width: 100%; "
        "height: 100%; top: 0; overflow: hidden; z-index: 98;display: block; "
        "cursor:pointer' onclick=\"adcase_click()\" ></div>"
        "<script>function adcase_click() { window.top.postMessage({ "
        "msg: 'adcase_click', format:'" + format_name + "' }, '*'); "
        "window.open(clickTag, '_blank')}</script>")
  else:
    v["clicktag_layer"] = ""

  ## replace all vars
  for name in v:
    index = index.replace("[[" + name + "]]", str(v[name]))

  # save modified index.html
  f.file_put_contents(build["dir"] + "/index.html", index)

  # create new zipfile
  if "size" not in build:
    build["size"] = f.get_param("size")

  file_name = (
      format_name + "_" + v["width"] + "x" + v["height"] + "_u" + user_id +
      "_id" + new_id + ".zip")
  if not f.create_zip(build["dir"], "/tmp/" + str(file_name)):
    build["errors"].append("Could not create zip file")

  f.clean_tmp(build["dir"])

  # upload to storage
  destination_file = "f/" + user_id + "/" + file_name
  ad_url = f.save_to_storage("/tmp/" + file_name, destination_file)
  if not ad_url:
    build["errors"].append("Could not save to storage")

  # save creative to DB
  save_process(user_id, new_id, format_id, ad_url)

  out = {"ok": True, "ad_url": ad_url, "user_id": user_id}
  if has_errors(build):
    out["errors"] = build["errors"]

  return jsonify(out)


def has_errors(build):
  """Checks if there are errors present.

  Args:
    build: the whole build object

  Returns:
    True if has errors, else False
  """
  return "errors" in build and len(build["errors"])


def save_process(user_id, file_id, format_id, ad_url):
  """Builder entry point.

  Dinamycally loads builder module.

  Args:
    user_id: format to build
    file_id: flask request
    format_id: flask request
    ad_url: action executed
  """
  db.query(
      "INSERT into creatives set user_id=%s, file_id=%s, format=%s,"
      "url=%s,created_date=now()", (user_id, file_id, format_id, ad_url))
  register_analytics(user_id, format_id, "build")


def register_analytics(user_id, format_id, action):
  """Builder entry point.

  Dinamycally loads builder module.

  Args:
    user_id: format to build
    format_id: flask request
    action: action executed
  """
  qty = db.res_int(
      "SELECT qty from analytics where date=curdate() and "
      "user_id=%s and format=%s and action=%s", (user_id, format_id, action))

  if qty > 0:
    sql = ("UPDATE analytics set qty=qty+1 where date=curdate() and "
           "user_id=%s and format=%s and action=%s")
  else:
    sql = ("INSERT into analytics set date=curdate(), "
           "year=date_format(now(),'%%Y'),month=date_format(now(),'%%m'),"
           "day=date_format(now(),'%%d'),dow=date_format(now(),'%%w'),"
           " user_id=%s,format=%s,action=%s,qty=1")
  db.query(sql, (user_id, format_id, action))
