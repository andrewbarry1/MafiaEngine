#!/usr/bin/python


import web, os, time, re, random


web.config.debug = False

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
        return render.new()
    
    
class game:
    def GET(self, game_number):
        # TODO check if game is open
        return render.game(game_number)
