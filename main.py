#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Content(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class MainHandler(Handler):
    def get(self):
        self.redirect("/blog")

class MainPage(Handler):
    def render_main(self, title="", content="", error=""):
        contents = db.GqlQuery("SELECT * FROM Content "
                               "ORDER BY created DESC "
                               "LIMIT 5 OFFSET 0")

        self.render("mainblog.html", title=title, content=content, error=error, contents=contents)

    def get(self):
        self.render_main()

class NewPost(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            a = Content(title = title, content = content)
            a.put()
            number=a.key().id()
            string="/blog/{0}".format(number)
            self.redirect(string)
        else:
            error = "You need both a title and content for your post!"
            self.render("newpost.html", title=title, content=content, error=error)

class ViewPostHandler(Handler):
    def get(self, id):
        post = Content.get_by_id(int(id))
        if not post:
            self.error(404)
            return
        self.render("post.html", post=post)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', MainPage),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
    #('/blog/ <id:\d+>'', ViewPostHandler)
], debug=True)
