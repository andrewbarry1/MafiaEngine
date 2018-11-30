#!/usr/bin/python

import web, os, time, re, random

web.config.debug = True

base = "/var/www/mafia/"

urls = (
    '/','index',
    '/game/(.*)', 'game'
)

app = web.application(urls, globals(), autoreload=True)
application = app.wsgifunc()

render = web.template.render(base + 'templates/')

class index:
    def GET(self):
        return render.index()
    
class game:
    def GET(self, game_number):
        return render.game(game_number)
