// Copyright 2019 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
w.values = {};
w.run_hash = null;

/** called by google auth */
check_login = function() {
  w.check_login();
};


/** execute logout */
w.sign_out = function() {
  $('#loading').hide();
  $('#main_container').hide();
  $('#signout').hide();
  $('#g-signin2').show();
  localStorage.removeItem('token');
  localStorage.removeItem('hash');
  localStorage.removeItem('userName');
  $('#user_name').html('');

  var auth2 = gapi.auth2.getAuthInstance();
  w.run_hash = null;
  auth2.signOut().then(function() {
    document.location.href = '/builder/100-html5';
  });
};


/** check if user is logged */
w.check_login = function() {
  try {
    var auth2 = gapi.auth2.getAuthInstance();
    var user = auth2.currentUser.get().getBasicProfile();

    if (typeof user == 'object' && typeof user.getEmail() == 'string') {
      $('#g-signin2').hide();
      $('#signout').show();

      var token = auth2.currentUser.get().getAuthResponse().id_token;

      if (localStorage.getItem('token') == token) {
        w.run();
      } else {
        $.post('/builder/login/register_token?token=' + token, {}, function(d) {
          if (d.user && d.user.name) {
            localStorage.setItem('token', token);
            localStorage.setItem('hash', d.user.hash);
            localStorage.setItem('userName', d.user.name);
            document.location.href = '?';
          } else {
            w.sign_out();
          }
        });
      }
    } else {
      $('#g-signin2').show();
      $('#signout').hide();
      $('#main_container').hide();
      $('#please_sign_in').show();
    }
  } catch (e) {
    $('#g-signin2').show();
    $('#signout').hide();
    $('#main_container').hide();
    $('#please_sign_in').show();
  }
};


/** show main screen */
w.run = function() {
  w.hash = localStorage.getItem('hash');
  if (w.run_hash != w.hash) {
    w.run_hash = w.hash;
    $('#user_name').html(localStorage.getItem('userName'));
    $('#g-signin2').hide();
    $('#signout').show();

    $('#please_sign_in').hide();
    w.get_sizes();
  }
};


/** get sizes defined for user */
w.get_sizes = function() {
  $.ajax({
    url: '/builder/sizes?hash=' + w.hash,
    success: function(d) {
      w.get_sizes2(d.sizes);
    },
    dataType: 'json'
  });
};


/**
get sizes defined for user (on success)
@param {?Object} sizes
*/
w.get_sizes2 = function(sizes) {
  for (var i in sizes) {
    var format_id = i.split('-')[0];
    if (format_id == w.format_id) {
      var field_name = i.split('-')[1];
      w.set_field_options(field_name, sizes[i]);
    }
  }
  $('ul').show();
  $('#loading').hide();
  $('#main_container').show();

  // paint selected format ul>li
  var u = document.location.href.split('?')[0].split('/');
  $('#' + u[u.length - 1]).css('background-color', '#ddd')
};


/**
set select values depending on user options
@param {string} field_name
@param {?Object} options
*/
w.set_field_options = function(field_name, options) {
  if ($('select[name=' + field_name + ']').length == 0) {
    return;
  }
  var select = document.forms[0][field_name];
  select.style.float = 'left';
  select.innerHTML = '';
  var options = options.split(',');
  for (var i in options) {
    if (options[i] != '') {
      var opt = document.createElement('option');
      opt.value = options[i];
      opt.innerHTML = options[i];
      select.appendChild(opt);
    }
  }

  var e = document.createElement('div');
  e.innerHTML = '<button class="edit_button" id="editButton_' + field_name +
      '" onclick="w.edit_options(`' + field_name + '`,`' + options +
      '`)">Edit</button>';
  e.style.float = 'left';
  e.style.verticalAlign = 'middle';
  e.style.padding = '0 20px 0 20px';
  select.parentElement.appendChild(e);
};


/**
build edit field for changing user sizes
@param {string} field_name
@param {?Object} sizes
*/
w.edit_options = function(field_name, sizes) {
  var e = document.createElement('div');
  e.innerHTML = 'Enter Values separated by commas:<br><textarea id="options_' +
      field_name + '" style=\"min-width:400px;width:100%;height:100px\">' +
      sizes + '</textarea><button onclick="w.save_options(`' + field_name +
      '`)">Save</button>';
  e.style.padding = '15px';
  document.forms[0][field_name].parentElement.appendChild(e);
  document.forms[0][field_name].parentElement.style.backgroundColor =
      ' #bae1ff';
  document.getElementById('editButton_' + field_name).style.display = 'none';
};


/**
seve user sizes for specific field
@param {string} field_id
*/
w.save_options = function(field_id) {
  $.ajax({
    url: '/builder/sizes',
    method: 'POST',
    data: {
      format_id: w.format_id,
      field_name: field_id,
      values: $('#options_' + field_id).val(),
      hash: w.hash
    },
    success: function(d) {
      document.location.href = '?'
    },
    dataType: 'json'
  });
};


/** submit a creative */
w.submit = function() {
  var form = new FormData($('#builderForm')[0]);
  form.append('hash', w.hash);

  $.ajax({
    url: '/builder/build/' + w.fmt,
    method: 'POST',
    dataType: 'json',
    data: form,
    processData: false,
    contentType: false,
    success: function(result) {
      if (result.errors) {
        alert(result.errors[0]);
      } else {
        var html = '<button onclick=\'document.location.href=`' +
            result.ad_url +
            '`\' class=\'btn btn-success\'>Download Creative</button>';
        $('#download_button').html(html);
      }
    },
    error: function(er) {
      if (er && er.responseJSON && er.responseJSON.errors &&
          er.responseJSON.errors[0]) {
        alert(er.responseJSON.errors[0]);
      } else {
        alert('Error in form. Please review all values');
      }
    }
  });
};


/**
redirect to url
@param {string} url
*/
w.go = function(url) {
  document.location.href = url;
};

if (localStorage.getItem('hash')) {
  w.run();
} else {
  check_login();
}
