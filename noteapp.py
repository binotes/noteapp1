# encoding: utf-8
#-------------------------------------------------------------------------------
# Name:        noteApp
# Purpose:     A simple note keeping app useing wsgi
#
# Author:      bin
#
# Created:     11/04/2025
# Copyright:   (c) bin 2025
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python


from wsgiref.simple_server import make_server
from urlparse import parse_qs
import codecs
import os
import datetime
import json

PORT =8000
NOTE_FILE = 'notes.json'

def load_notes():
#try:
    with codecs.open(NOTE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)
    #except:
    #    return ['open notes  fails']

def save_notes(notes):
    with codecs.open(NOTE_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=4)


def read_template(template_file='index.html'):
    try:
        with codecs.open(template_file, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ['open template file fails']

def generate_notes_html(notes):
    html = u""
    for note in notes:
        html += '<li> %s </li>' % note
    return html

def generate_admin_html(notes):
    html = u""
    for index,note in enumerate(notes):
        html += '<li> %s <a href="delete?index=%s">del</a> &nbsp <a href="edit?index=%s">edit</a></li>' % (note,index,index)
    return html


def application(environ, start_response):
    method = environ['REQUEST_METHOD']
    path = environ['PATH_INFO']

    if path == '/' and method == 'GET':
        return home(environ, start_response)
    elif path == '/add' and method == 'POST':
        return add_note(environ, start_response)
    else:
        return err_404(environ, start_response)

def home(environ, start_response):
    notes = load_notes()
    notes_html = generate_notes_html(notes)
    html_template = read_template()
    html = html_template.replace('{{ notes }}', notes_html)
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    return [html.encode('utf-8')]

def add_note(environ, start_response):    
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(request_body_size)
        post_data = parse_qs(request_body) # 解码为字符串
        note_content = post_data['note'][0].decode('utf-8')  # 获取笔记内容
    except (ValueError, KeyError):
        note_content = u'no note content'
    cur_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 获取当前日期和时间
    note_with_date = cur_date + ': ' + note_content  # 拼接日期和笔记内容
    notes = load_notes()
    notes.append(note_with_date)  # 直接添加笔记内容
    save_notes(notes)
    start_response('302 Found', [('Location', '/')])
    return []
    
    

def err_404(environ, start_response):
    status = '404 Not Found'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    return [b'page not found!']



"""
ver1 just start srv
"""
def run_server():
    srv = make_server('0.0.0.0', PORT, application)
    print('servring at port : %s' % PORT)
    srv.serve_forever()

if __name__ == '__main__':
    run_server()

