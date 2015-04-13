import os,sys
sys.path.insert(0, 'lib')
from google.appengine.api import users
import webapp2
import errno
import datetime
from google.appengine.ext import db
import json
from lib.googleapiclient.discovery import build
import six
import random
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow
import httplib2
from oauth2client.file import Storage
from google.appengine.ext import db
from oauth2client.appengine import CredentialsProperty
from oauth2client.appengine import StorageByKeyName
http = httplib2.Http()
import uuid


class Super:
    current_job = ""
    train_key = ""

class CredentialsModel(db.Model):
    credentials = CredentialsProperty()

flow = flow_from_clientsecrets('gsoc-cloud-cv-2fd4577c20c3.json',
                               scope='https://www.googleapis.com/auth/bigquery https://www.googleapis.com/auth/userinfo.email',
                               redirect_uri='http://vatsal-gsoc-cloud-cv.appspot.com/oauth2callback'
                               # redirect_uri='http://localhost:8080/oauth2callback'
        )

class Auth():

    def get_auth_uri(self):
        print "get_auth_uri"
        return str(flow.step1_get_authorize_url())

    def handle_auth_uri_response(self, code):
        print "handle_auth_uri_response"
        auth_code = str(code)
        creds = flow.step2_exchange(auth_code)
        gd_token = uuid.uuid4()
        access_token = json.loads(creds.to_json())['access_token']
        email = json.loads(creds.to_json())['id_token']['email']
        domain = '*@'+email.split("@")[1]
        storage = StorageByKeyName(CredentialsModel, str(gd_token), 'credentials')
        storage.put(creds)
        return (str(gd_token),access_token, email)

class Login(webapp2.RequestHandler):
    def get(self):
        Super.current_job = ""
        Super.train_key = ""
        a = Auth()
        print "Controller Auth :"+str(a)
        auth_uri = a.get_auth_uri()
        print "Controller Auth URI :"+str(auth_uri)
        return self.redirect(auth_uri)

class Authrzd(webapp2.RequestHandler):
    def get(self):
        a=Auth()
        (uuid, token, email) = a.handle_auth_uri_response(self.request.get('code'))
        self.response.set_cookie('user',email, max_age=360)
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(open('templates/authorized.html').read())

class File(webapp2.RequestHandler):
    def post(self):
        d = json.loads(self.request.body)
        email = self.request.cookies.get('user')
        search = d.get("search")
        print Super.current_job
        if Super.current_job == "":
            obj = instantiate_job(email,search)
            Super.current_job = obj['job_id']
            Super.train_key = obj['train_key']

        cat = Category(parent = Super.train_key)
        cat.id = search
        cat.put()

        links = getLinks(search)
        json_links = json.loads(links)

        for itr in json_links['links']:
            img = Images(parent = cat)
            img.id = search
            img.name = itr['title']
            img.mime = itr['mime'] 
            img.picture = itr['link']
            img.thumb = itr['thumblink']
            img.put()

        response = {'job_id':Super.current_job,'links':json_links}
        return webapp2.Response(json.dumps(response))

class Job(db.Model):
  job_name = db.StringProperty()
  job_date = db.DateProperty()
  user =  db.StringProperty()

class Train(db.Model):
  id = db.StringProperty()

class Test(db.Model):
  id = db.StringProperty()

class Util(db.Model):
  id = db.StringProperty()

class Category(db.Model):
  id = db.StringProperty()

class Images(db.Model):
  id = db.StringProperty()
  name = db.StringProperty()
  mime = db.StringProperty()
  picture = db.LinkProperty()
  thumb = db.LinkProperty()
  # picture = db.BlobProperty(default=None)
  # thumb = db.BlobProperty(default=None)

class Start(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(open('templates/index.html').read())
     
class SetJob(webapp2.RequestHandler):
    def post(self):
        d = json.loads(self.request.body)
        v = d.get("job_id")
        Super.current_job = v

        q = Train.all()
        p1 = db.Key.from_path('Job', v)
        q.ancestor(p1)
        key = ""
        for p in q.run():
            key = p.key()

        Super.train_key = key

class ListJob(webapp2.RequestHandler):
    def post(self):
        q = Job.all()
        jodid_list = []
        for p in q.run():
            if(p.user == self.request.cookies.get('user')):
                jodid_list.append(p.job_name)

        res = {'list':jodid_list}
        return webapp2.Response(json.dumps(res))

class ViewCat(webapp2.RequestHandler):
    def post(self):
        q = Train.all()
        p1 = db.Key.from_path('Job', Super.current_job)
        q.ancestor(p1)
        key = ""
        for p in q.run():
            key = p.key()

        q = Category.all()
        p1=db.get(key)
        q.ancestor(p1)
        cat = []
        for p in q.run():
            obj = {}
            obj['name'] = p.id
            obj['key'] = p.key()
            cat.append(obj)

        img_list = {}
        for i in cat:
            q = Images.all()
            p1=db.get(i['key'])
            q.ancestor(p1)
            arr = []
            for p in q.run():
                arr.append(p.thumb)
            img_list[i['name']] = arr

        return webapp2.Response(json.dumps(img_list))

def getLinks(word):
    service = build("customsearch", "v1", developerKey="AIzaSyAhtD_QM5-JpevrsXjYvhcXCLy7WzKIwu8")
    res = service.cse().list(
            q=word,
            cx='004198854479581006327:u-khh8gfoma',
            searchType='image'
        ).execute()
    obj = {'links':[]}
    if not 'items' in res:
        print 'No result !!\nres is: {}'.format(res)
    else:
        for itr in res['items']:
            obj2 = {}
            obj2['title'] = itr['title']
            obj2['link'] = itr['link']
            obj2['mime'] = itr['mime']
            obj2['thumblink'] = itr['image']['thumbnailLink']
            obj['links'].append(obj2)
    return json.dumps(obj)

def instantiate_job(email,search):
    today = datetime.datetime.now()
    date = (today + datetime.timedelta(hours=5, minutes=30)).strftime("%Y/%m/%d__%I:%M_%p")
    key = email+str(random.randint(1, 1000)) +"_"+date

    job = Job(key_name=key,job_name=key,user=email)
    job.job_date = datetime.datetime.now().date()
    job.put()
    print 
    train = Train(parent = job)
    train.key_name = key        
    train.id = key
    train.put()

    return {'job_id':key,'train_key':train.key()}

        
app = webapp2.WSGIApplication([
    ('/', Start),
    ('/file', File),
    ('/login',Login),
    ('/listjob',ListJob),
    ('/setjob',SetJob),
    ('/viewcat',ViewCat),
    ('/oauth2callback',Authrzd)
], debug=True)