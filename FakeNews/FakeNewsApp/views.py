from django.shortcuts import render
from django_file_md5 import calculate_md5
from random import choice as oldchoice
from numpy.random import choice
from string import digits
from datetime import datetime
from django.contrib.auth.models import User
from .models import Reader, Journalist, Auditor, Article, StakeTransaction, Comment, Like
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
import os, requests, json
MEDIA_URL = '/media/'


def generate_random_username(length=12, chars=digits):
    username = [oldchoice(chars) for i in range(length)]
    try:
        User.objects.get(username=username)
        return generate_random_username(length=length, chars=chars)
    except User.DoesNotExist:
        return "".join(username);

def login_check(request, entered_email, entered_password):
    if User.objects.filter(email=entered_email).exists():
        username = User.objects.get(email=entered_email.lower()).username
        user = authenticate(username=username, password=entered_password)
        if user is not None:
            login(request, user)
            return "TRUE"
        else:
            return "Incorrect credentials"
    else:
        return "No account exists"

def signup_check(request, entered_email, entered_password, entered_fname, entered_lname, entered_type, entered_idproof):
    if User.objects.filter(email=entered_email).exists():
        return "Account already exists"
    else:
        user = User.objects.create_user(
                    username = generate_random_username(),
                    password = entered_password,
                    email = entered_email
                    )
        if entered_type == "AAA":
            auditor = Auditor.objects.create(
                id = user,
                fname = entered_fname,
                lname = entered_lname,
                idproof = entered_idproof,
            )
            user.save()
            auditor.save()
        elif entered_type == "JJJ":
            journalist = Journalist.objects.create(
                id = user,
                fname = entered_fname,
                lname = entered_lname,
                idproof = entered_idproof,
            )
            user.save()
            journalist.save()
        else:
            reader = Reader.objects.create(
                id = user,
                fname = entered_fname,
                lname = entered_lname,
            )
            user.save()
            reader.save()
        login(request, user)
        return "TRUE"

def newsArticleCheck(headline, body):
    resp = requests.post("http://localhost:5000/check", {"headline":headline, "body":body})
    if resp.text == "Fake":
        return False
    else:
        return True


def index(request):
    return HttpResponse( "Home Page" )



def findType(user):
    if Journalist.objects.filter(id=user).exists():
        return("JJJ", Journalist.objects.get(id=user))
    elif Auditor.objects.filter(id=user).exists():
        return("AAA", Auditor.objects.get(id=user))
    elif Reader.objects.filter(id=user).exists():
        return("RRR", Reader.objects.get(id=user))
    else:
        return ("None", None)


@login_required(login_url='/login')
def logoutView(request):
    logout(request)
    return HttpResponseRedirect("/")


def loginView(request):
    if request.method == 'POST':
        entered_email = request.POST.get('login_email')
        entered_password = request.POST.get('login_password')
        reply = login_check(request, entered_email, entered_password)
        if reply == 'TRUE':
            return HttpResponseRedirect('/profile')
        else:
            return render(request, "FakeNewsApp/login-register.html", {"error":reply})
    else:
        return render(request, "FakeNewsApp/login-register.html")

def signupView(request):
    if request.method == 'POST':
        entered_email = request.POST.get('signup_email')
        entered_password = request.POST.get('signup_password')
        entered_type = request.POST.get('signup_type')
        entered_fname = request.POST.get('signup_fname')
        entered_lname = request.POST.get('signup_lname')
        if entered_type == "JJJ" or entered_type == "AAA":
            entered_idproof = request.FILES["signup_idproof"]
        else:
            entered_idproof = None
        print(entered_idproof)
        reply = signup_check(request, entered_email, entered_password, entered_fname, entered_lname, entered_type, entered_idproof)
        if reply == 'TRUE':
            return HttpResponseRedirect('/profile')
        else:
            return render(request, "FakeNewsApp/login-register.html", {"error":reply})
    else:
        return render(request, "FakeNewsApp/login-register.html")



def get_most_liked(all):
    likes = 0
    try:
        article = all[0]
        for a in all:
            if a.get_likes() > likes:
                likes = a.get_likes()
                article = a
        return (article, likes)
    except:
        return (None, 0)

@login_required(login_url='/login')
def profile(request):
    a ,b = findType(request.user)
    if a == "RRR":
        allarts = Article.objects.filter(audit_status=True).order_by('-block_time')
        context = {
            "allarts": allarts,
            "MEDIA_URL": MEDIA_URL,
            "reader": b,
        }
        return render(request, "FakeNewsApp/readerprof.html", context)
    elif a == "JJJ":
        all_articles = Article.objects.filter(journalist=b).order_by('-post_time')
        completed = list()
        pending = list()
        for d in all_articles:
            if d.block_time and d.audit_completed and d.audit_status:
                completed.append(d)
            elif not d.audit_completed:
                pending.append(d)
        top_liked, likes_no = get_most_liked(completed)
        context = {
            "completed": completed,
            "pending": pending,
            # "top_liked": top_liked,
            "likes_no": likes_no,
            "journalist": b,
            "MEDIA_URL": MEDIA_URL,
            'no_articles_published': len(completed)
        }
        return render(request, "FakeNewsApp/profile-journo.html", context)
    elif a == "AAA":
        completed = Article.objects.filter(auditor=b, audit_status=True).order_by('-post_time')
        pending = Article.objects.filter(auditor=b, audit_completed=None).order_by('-post_time')
        completed_no = len(completed)
        assigned_no = len(pending) + completed_no
        context = {
            "completed": completed,
            "pending": pending,
            "completed_no": completed_no,
            "assigned_no": assigned_no,
            "MEDIA_URL": MEDIA_URL,
            "auditor": b,
        }
        return render(request, "FakeNewsApp/audprofile.html", context)
    else:
        return HttpResponseRedirect("/logout")
    


def addToBLockchain(articleID):
    article = Article.objects.get(id=articleID)
    md5 = calculate_md5(article.img)
    data = {
        "headline": str(article.headline),
        "body": str(article.body),
        "src": str(article.src),
        "postTime": str(article.post_time),
        "approvalTime": str(article.audit_completed),
        "journalist": str(article.journalist.id.username),
        "auditor": str(article.auditor.id.username),
        "articleID": str(article.id),
        "img" : str(md5),
    }
    resp = requests.post("http://localhost:3001/mineBlock", json=data)
    if resp.text == "Success":
        article.block_time = datetime.now()
        article.save()
    elif resp.text == "Failed":
        pass

def selectAuditor():
    allAuditors = Auditor.objects.filter(verified=True)
    allStakes = [a.get_stake() for a in allAuditors]
    z =  sum(allStakes)
    allStakes[:] = [x / z for x in allStakes]
    selected_auditor = choice(allAuditors, 1, p=allStakes)
    return selected_auditor[0]




def homeView(request):
    arts = articleExtractor()
    return render(request, "FakeNewsApp/main-page.html", {"MEDIA_URL": MEDIA_URL, "articles":arts})


@login_required(login_url='/login')
def articleView(request, artid):
    a, b = findType(request.user)
    try:
        article = Article.objects.get(id=artid)
        allarts = Article.objects.all().order_by('-block_time')
        comments = article.get_comments()
        a, b = findType(request.user)
        context = {
            "article":article,
            "MEDIA_URL": MEDIA_URL,
            "user_type":a,
            "no_comments": len(comments),
            "comments": comments,
            "likes": article.get_likes(),
            "tops1":allarts[0:3],
            "tops2":allarts[3:5],
        }
        if a == "RRR":
            try:
                c = Like.objects.get(reader=b, article=article)    
                context["is_liked"] = True 
            except:
                context["is_liked"] = False
        return render(request, "FakeNewsApp/article.html", context)
    except:
        return HttpResponse("Article does not exist")


@login_required(login_url='/login')
def articleUpload(request):
    a, b = findType(request.user)
    if a == "JJJ":
        if request.method == "GET":
            if b.is_activated():
                return render(request, "FakeNewsApp/upload.html", {"journalist":b})
            else:
                return render(request, "FakeNewsApp/uploaderror.html", {"error": "You cannot upload any article"})
                # return HttpResponse("You cannot upload any article")
        elif request.method == "POST":
            if b.is_activated():
                entered_headline = request.POST.get("entered_headline")
                entered_body = request.POST.get("entered_body")
                entered_src = request.POST.get("entered_src")
                entered_img = request.FILES["entered_img"]
                if newsArticleCheck(entered_headline, entered_body):
                    print("ML Passed, Selecting Auditor..")
                    selected_auditor = selectAuditor()
                    article = Article.objects.create(
                        headline = entered_headline,
                        body = entered_body,
                        journalist = b,
                        src = entered_src,
                        img = entered_img,
                        auditor = selected_auditor,
                        post_time = datetime.now(),
                        audit_requested = datetime.now(),
                    )
                    article.save()
                    print("ML Passed, Audit requested from "+ str(selected_auditor.id.email) + " --- " + str(selected_auditor)  + " who has a stake of "+ str(selected_auditor.get_stake()))
                    return HttpResponseRedirect("/profile")
                else:
                    # return HttpResponse("Article Declined by algorithm")
                    return render(request, "FakeNewsApp/uploaderror.html", {"error": "Article Declined by algorithm"})
            else:
                # return HttpResponse("You cannot upload any article")
                return render(request, "FakeNewsApp/uploaderror.html", {"error": "You cannot upload any article"})
        else:
            # return HttpResponse("You cannot upload any article")
            return render(request, "FakeNewsApp/uploaderror.html", {"error": "You cannot upload any article"})
    else:
        # return HttpResponse("You cannot upload any article")
        return render(request, "FakeNewsApp/uploaderror.html", {"error": "You cannot upload any article"})


@login_required(login_url='/login')
def stakeView(request):
    a, b = findType(request.user)
    if a == "AAA":
        if request.method == "GET":
            return render(request, "FakeNewsApp/stake.html", {"auditor": b, "cur_stake": b.get_stake()})
        else:
            entered_amt = request.POST.get("entered_amt")
            entered_tt = request.POST.get("entered_tt")
            tran = StakeTransaction.objects.create(
                amount = entered_amt,
                tranType = entered_tt,
                auditor = b,
            )
            tran.save()
            return render(request, "FakeNewsApp/stake.html", {"auditor": b, "cur_stake": b.get_stake()})
    else:
        return HttpResponse("No access")



@login_required(login_url='/login')
def auditView(request, artid):
    a, b = findType(request.user)
    if a == "AAA":
        if request.method == "POST":
            art = Article.objects.get(id=artid)
            dec = request.POST.get("decision")
            if dec == "approve":
                art.audit_completed = datetime.now()
                art.audit_status = True
                art.save()
                addToBLockchain(artid)
                return HttpResponseRedirect("/profile")
            else:
                art.audit_status = False
                art.audit_completed = datetime.now()
                art.save()
                return HttpResponseRedirect("/profile")
        else:
            return render(request, "FakeNewsApp/auditing.html", {"auditor":b, "MEDIA_URL": MEDIA_URL, "article": Article.objects.get(id=artid) })
    else:
        return HttpResponse("No access")


def articleExtractor(n=3):
    arts = Article.objects.all().order_by('-block_time')
    arts = [a for a in arts if a.block_time]
    try:
        return arts[:n]
    except:
        return arts



def restored_blockchain(request):
    arts = Article.objects.all().order_by('block_time')
    for article in arts:
        md5 = calculate_md5(article.img)
        data = {
            "headline": str(article.headline),
            "body": str(article.body),
            "src": str(article.src),
            "postTime": str(article.post_time),
            "approvalTime": str(article.audit_completed),
            "journalist": str(article.journalist.id.username),
            "auditor": str(article.auditor.id.username),
            "articleID": str(article.id),
            "img" : str(md5),
        }
        resp = requests.post("http://localhost:3001/mineBlock", json=data)
        if resp.text == "Success":
            print("Block restored")
    return HttpResponseRedirect("/")


def likeInterface(request):
    if request.method=='POST':
        rec_id = int(request.POST.get('user_id'))
        reader = Reader.objects.get(id=User.objects.get(username=rec_id))
        print(request.POST.get('article_id'))
        article = Article.objects.get(id=request.POST.get('article_id'))
        if request.POST.get('islike') == "yes":
            try:
                a = Like.objects.get(reader=reader, article=article)
            except:
                newlike = Like.objects.create(reader=reader, article=article)
                newlike.save()
            return JsonResponse({'new_likes':article.get_likes(), 'islike':"yes"})            
        elif request.POST.get('islike') == "no":
            try:
                Like.objects.get(reader=reader, article=article).delete()
            except:
                pass
            return JsonResponse({'new_likes':article.get_likes(), 'islike':"no"})


@login_required(login_url='/login')
def postComment(request):
    if request.method == 'POST':
        try:
            newcomment = Comment.objects.create(
                comment = request.POST.get('comment_text'),
                reader = Reader.objects.get(id=request.user),
                article = Article.objects.get(id=request.POST.get('article_id'))
                )
            newcomment.save()
            return HttpResponseRedirect("/article/"+request.POST.get('article_id'))
        except:
            return HttpResponseRedirect("/article/"+request.POST.get('article_id'))
    else:
        return HttpResponseRedirect("/")


@login_required(login_url='/login')
def latestNews(request):
    allarts = Article.objects.filter(audit_status=True).order_by('-block_time')
    a ,b = findType(request.user)
    context = {
        "allarts": allarts,
        "MEDIA_URL": MEDIA_URL,
    }
    if a == "RRR":
        return HttpResponseRedirect("/")
    elif a == "JJJ":
        context["journalist"] = b
        return render(request, "FakeNewsApp/jjjnews.html", context)
    elif a == "AAA":
        context["auditor"] = b
        return render(request, "FakeNewsApp/aaanews.html", context)
    