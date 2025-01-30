from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from .models import User, Post, Follow, Like

def unlike(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    like = Like.objects.filter(user=user, post=post)
    like.delete()

    return JsonResponse({"message": "Like deleted successfully!", "likes": post.likes})

def like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    like = Like(user=user, post=post)
    like.save()
    
    return JsonResponse({"message": "Like added successfully!", "likes": post.likes})

def edit(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        editPost = Post.objects.get(pk=post_id)
        editPost.content = data["content"]
        editPost.save()
        return JsonResponse({"message": "Changed successfully", "data": data["content"]})

def index(request):
    posts= Post.objects.all().order_by("id").reverse()

    paginator = Paginator(posts, 10)
    pageNum = request.GET.get('page')
    postsInPage = paginator.get_page(pageNum)

    likes = Like.objects.all()

    likedPosts = []

    try:
        for like in likes:
            if like.user.id == request.user.id:
                likedPosts.append(like.post.id)
    except:
        likedPosts = []

    return render(request, "network/index.html", {
        "postsInPage": postsInPage,
        "likedPosts": likedPosts
    })

def newPost(request):
    if request.method == "POST":
        content = request.POST['content']
        user = User.objects.get(pk=request.user.id)
        post = Post(content=content, user=user)
        post.save()
        return HttpResponseRedirect(reverse(index))

def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    posts= Post.objects.filter(user=user).order_by("id").reverse()

    following = Follow.objects.filter(user=user)
    follower = Follow.objects.filter(follower=user)

    try:
        checkFollow = follower.filter(user=User.objects.get(pk=request.user.id))

        if len(checkFollow) != 0:
            isFollowing = True
        else :
            isFollowing = False
    except:
        isFollowing = False

    paginator = Paginator(posts, 10)
    pageNum = request.GET.get('page')
    postsInPage = paginator.get_page(pageNum)

    return render(request, "network/profile.html", {
        "postsInPage": postsInPage,
        "username": user.username,
        "user": user,
        "following": following,
        "follower": follower,
        "isFollowing": isFollowing
    })

def following(request):
    currentUser = User.objects.get(pk=request.user.id)
    following = Follow.objects.filter(user=currentUser)
    posts = Post.objects.all().order_by('id').reverse()

    postsFollowing = []
    
    for post in posts:
        for follow in following:
            if follow.follower == post.user:
                postsFollowing.append(post)

    paginator = Paginator(postsFollowing, 10)
    pageNum = request.GET.get('page')
    postsInPage = paginator.get_page(pageNum)

    return render(request, "network/following.html", {
        "postsInPage": postsInPage
    })

def follow(request):
    follow = request.POST['follow']
    currentUser = User.objects.get(pk=request.user.id)
    userFollowData = User.objects.get(username=follow)
    f = Follow(user=currentUser, follower=userFollowData)
    f.save()
    user_id = userFollowData.id
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id':user_id}))

def unfollow(request):
    follow = request.POST['follow']
    currentUser = User.objects.get(pk=request.user.id)
    userFollowData = User.objects.get(username=follow)
    f = Follow.objects.get(user=currentUser, follower=userFollowData)
    f.delete()
    user_id = userFollowData.id
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id':user_id}))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
