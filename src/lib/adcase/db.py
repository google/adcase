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
"""Mysql DB helper."""
import os
import pymysql
from flask import g

def close_connection():
  """Closes g.connection."""
  try:
    g.cursor.close()
  except pymysql.err.InternalError:
    pass

  try:
    g.connection.close()
  except pymysql.err.InternalError:
    pass


def open_connection():
  """Opens g.connection."""
  if os.environ.get('CLOUD_SQL_CONNECTION_NAME'): 
    g.connection = pymysql.connect(
      user=os.environ.get('CLOUD_SQL_USERNAME'),
      password=os.environ.get('CLOUD_SQL_PASSWORD'),
      unix_socket=os.environ.get('CLOUD_SQL_CONNECTION_NAME'),
      db=os.environ.get('CLOUD_SQL_DATABASE_NAME'),
      host=os.environ.get('CLOUD_SQL_HOST')
      )
  else:
    g.connection = pymysql.connect(
      user=os.environ.get('CLOUD_SQL_USERNAME'),
      password=os.environ.get('CLOUD_SQL_PASSWORD'),
      db=os.environ.get('CLOUD_SQL_DATABASE_NAME'),
      host=os.environ.get('CLOUD_SQL_HOST')
      )

  g.cursor = g.connection.cursor()


def full_res(sql, params=None):
  """Returns full dataset.

  Args:
    sql: SELECT string
    params: params to update the query

  Returns:
    Array of records
  """
  out = []
  try:
    g.cursor.execute(sql, params)
    fields = []
    for f in g.cursor.description:
      fields.append(f[0])
    for r in g.cursor.fetchall():
      row = {}
      for f in range(0, len(fields)):
        row.update({fields[f]: r[f]})
      out.append(row)
  except pymysql.err.InternalError:
    pass
  return out


def first_row(sql, params=None):
  """Returns first row of dataset.

  Args:
    sql: SELECT string
    params: params to update the query

  Returns:
    First record
  """
  out = {}
  try:
    g.cursor.execute(sql, params)
    fields = []
    for f in g.cursor.description:
      fields.append(f[0])
    r = g.cursor.fetchone()
    for f in range(0, len(fields)):
      out.update({fields[f]: r[f]})
  except pymysql.err.InternalError:
    pass
  return out


def query(sql, params=None):
  """Executes a query, i.e UPDATE or INSERT.

  Args:
    sql: SELECT string
    params: params to update the query

  Returns:
    Int, number of affected records
  """
  out = 0
  try:
    g.cursor.execute(sql, params)
    out = g.cursor.rowcount
    g.connection.commit()
  except pymysql.err.InternalError:
    pass
  return out


def res(sql, params=None):
  """Returns first field of first record of dataset.

  Args:
    sql: SELECT string
    params: params to update the query

  Returns:
    string with result
  """
  out = ''
  try:
    g.cursor.execute(sql, params)
    out = str(g.cursor.fetchone()[0])
  except pymysql.err.InternalError:
    pass
  except TypeError:
    pass
  return out


def res_int(sql, params=None):
  """Returns first field of first record of dataset as int.

  Args:
    sql: SELECT string
    params: params to update the query

  Returns:
    int with result
  """
  out = 0
  try:
    out = int(res(sql, params))
  except ValueError:
    pass
  except pymysql.err.InternalError:
    pass
  return out
