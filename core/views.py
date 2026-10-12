from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Bookmark, Profile
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm
from django.shortcuts import get_object_or_404, redirect
from .models import Post, Comment, Follow
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Count
from core.models import Conversation, Message
from django.db.models import Q
from .models import Notification







from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer




def create_notification(sender, recipient, notif_type, post=None, text=""):
    if sender == recipient:
        return

    notification = Notification.objects.create(
        sender=sender,
        recipient=recipient,
        notif_type=notif_type,
        post=post,
        text=text
    )

    # 🔥 REAL-TIME PUSH
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"notif_{recipient.id}",
        {
            "type": "send_notification",
            "data": {
                "sender": sender.username,
                "text": text,
                "type": notif_type,
            }
        }
    )

@login_required

def get_notifications(request):
    notifs = Notification.objects.filter(
        recipient=request.user
    ).order_by("-created_at")[:20]

    data = []

    for n in notifs:
        data.append({
            "id": n.id,
            "type": n.notif_type,
            "text": n.text,
            "sender": n.sender.username,
            "avatar": (
                n.sender.profile.profile_picture.url
                if hasattr(n.sender, "profile") and n.sender.profile.profile_picture
                else ""
            ),
            "time": n.created_at.strftime("%b %d, %H:%M")
        })

    return JsonResponse({"notifications": data})


@login_required
def mark_notifications_read(request):
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    return JsonResponse({"success": True})

def dashboard_search(request):
    q = request.GET.get("q", "")

    posts = Post.objects.filter(
        Q(caption__icontains=q) |
        Q(post_type__icontains=q) |
        Q(user__username__icontains=q)
    ).order_by("-created_at")

    # ✅ EMPTY RESULT CHECK (ADD THIS HERE)
    if not posts.exists():
        return JsonResponse({
            "html": ""
        })

    html = render_to_string("partials/posts.html", {
        "posts": posts
    }, request=request)

    return JsonResponse({
        "html": html
    })




def search(request):
    query = request.GET.get("q", "")

    users = User.objects.filter(username__icontains=query)[:10]

    posts = Post.objects.filter(
        Q(caption__icontains=query) |
        Q(user__username__icontains=query)
    ).order_by("-created_at")[:20]

    data = {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "avatar": (
                    u.profile.profile_picture.url
                    if hasattr(u, "profile") and u.profile.profile_picture
                    else ""
                )
            }
            for u in users
        ],
        "posts": [
            {
                "id": p.id,
                "username": p.user.username,
                "caption": p.caption,
                "image": p.image.url if p.image else ""
            }
            for p in posts
        ]
    }

    return JsonResponse(data)




def search_users(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"users": []})

    users = User.objects.filter(
        username__icontains=query
    ).exclude(id=request.user.id)[:10]

    results = []

    for u in users:
        conversation = Conversation.objects.filter(
            users=request.user
        ).filter(
            users=u
        ).first()

        last_message = None
        unread = 0

        if conversation:
            last_msg_obj = Message.objects.filter(
                conversation=conversation
            ).order_by("-created_at").first()

            if last_msg_obj:
                last_message = last_msg_obj.text

            unread = Message.objects.filter(
                conversation=conversation,
                is_read=False
            ).exclude(sender=request.user).count()

        results.append({
            "id": u.id,
            "username": u.username,
            "avatar": u.profile.profile_picture.url if hasattr(u, "profile") and u.profile.profile_picture else "",
            "conversation_id": conversation.id if conversation else None,
            "last_message": last_message,
            "unread": unread,
        })

    return JsonResponse({"users": results})









def load_feed(request):

    feed_type = request.GET.get("feed")

    if feed_type == "following":

        following_users = Follow.objects.filter(
            follower=request.user
        ).values_list(
            "following_id",
            flat=True
        )

        posts = Post.objects.filter(
            user_id__in=following_users
        ).order_by("-created_at")

    else:

        posts = Post.objects.all().order_by("-created_at")

    html = render_to_string(
        "partials/posts.html",
        {"posts": posts},
        request=request
    )

    return JsonResponse({
        "html": html
    })


def following_feed(request):

    following_users = Follow.objects.filter(
        follower=request.user
    ).values_list("following", flat=True)

    posts = Post.objects.filter(
        user__in=following_users
    ).order_by("-created_at")

    data = []

    for post in posts:
        data.append({
            "id": post.id,
            "username": post.user.username,
            "caption": post.caption,
            "likes": post.likes.count(),
        })

    return JsonResponse({"posts": data})




def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)

    follow = Follow.objects.filter(
        follower=request.user,
        following=target_user
    )

    if follow.exists():
        follow.delete()
        following = False
    else:
        Follow.objects.create(
            follower=request.user,
            following=target_user
        )
        following = True

        create_notification(
            sender=request.user,
            recipient=target_user,
            notif_type="follow",
            text=f"{request.user.username} started following you"
        )

    followers_count = Follow.objects.filter(
        following=target_user
    ).count()

    return JsonResponse({
        "following": following,
        "followers_count": followers_count,
    })


def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

        # 🔥 ADD THIS
        create_notification(
            sender=request.user,
            recipient=post.user,
            notif_type="like",
            post=post,
            text=f"{request.user.username} liked your post"
        )

    return JsonResponse({
        "likes": post.likes.count(),
        "liked": liked
    })



def add_comment(request, post_id):

    if request.method == "POST":

        post = get_object_or_404(Post, id=post_id)

        text = request.POST.get("text")

        if not text:
            return JsonResponse({"success": False})

        comment = Comment.objects.create(
            post=post,
            user=request.user,
            text=text
        )


        create_notification(
            sender=request.user,
            recipient=post.user,
            notif_type="comment",
            post=post,
            text=f"{request.user.username} commented on your post"
        )

        return JsonResponse({
            "success": True,
            "username": request.user.username,
            "text": comment.text,
            "comment_id": comment.id,
            "comment_count": comment.post.comments.count()
        })
    


def delete_comment(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id)

    post = comment.post

    if request.user == comment.user or request.user == post.user:

        new_count = post.comments.count() - 1

        comment.delete()

        return JsonResponse({
            "success": True,
            "comment_id": comment_id,
            "comment_count": new_count
        })

    return JsonResponse({
        "success": False
    }, status=403)


def bookmark_post(request, post_id):

    if request.method == "POST":

        post = get_object_or_404(Post, id=post_id)

        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            post=post
        )

        if not created:
            bookmark.delete()
            bookmarked = False
        else:
            bookmarked = True

        count = Bookmark.objects.filter(post=post).count()

        create_notification(
            sender=request.user,
            recipient=post.user,
            notif_type="save",
            post=post,
            text=f"{request.user.username} saved your post"
        )

        return JsonResponse({
            "success": True,
            "bookmarked": bookmarked,
            "count": count
        })

    return JsonResponse({
        "success": False
    })



@login_required
def update_profile_picture(request):
    if request.method == "POST":
        profile = request.user.profile

        if request.FILES.get("profilePhoto"):
            profile.profile_picture = request.FILES["profilePhoto"]
            profile.save()

    return redirect("settings") 

def index(request):
    return render(request, "index.html")

def login_view(request):
    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                return JsonResponse({
                    "success": True,
                    "redirect": "/dashboard/"
                })

            return JsonResponse({
                "success": False,
                "error": "Invalid email or password"
            })

        except User.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Invalid email or password"
            })

    return render(request, "login.html")

def signup(request):

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        profile_picture = request.FILES.get("profilePhoto")

        # validations
        if password1 != password2:
            return JsonResponse({
                "success": False,
                "error": "Passwords do not match"
            })

        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "success": False,
                "error": "Username already exists"
            })

        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "success": False,
                "error": "Email already exists"
            })

        # create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        names = full_name.split()
        user.first_name = names[0]
        user.last_name = " ".join(names[1:]) if len(names) > 1 else ""
        user.save()

        # create profile safely
        profile = Profile.objects.create(
            user=user,
            bio="✨ Welcome to my Pixera profile!"
        )

        if request.FILES.get("profilePhoto"):
            profile.profile_picture = request.FILES["profilePhoto"]
            profile.save()

        login(request, user)

        return JsonResponse({
            "success": True,
            "redirect": "/dashboard/"
        })

    return render(request, "signup.html")

def logout_view(request):
    logout(request)
    return redirect('index')




@login_required
def mark_notifications_read(request):

    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    return JsonResponse({
        "success": True
    })

@login_required

def dashboard(request):

    posts = Post.objects.all().order_by(
        '-created_at'
    ).prefetch_related(
        'comments',
        'likes'
    )

    top_creators = User.objects.annotate(
        post_count=Count("post")
    ).order_by("-post_count")[:5]

    trending_posts = Post.objects.annotate(
        likes_count=Count("likes")
    ).order_by("-likes_count")[:6]

    new_members = User.objects.order_by(
        "-date_joined"
    )[:3]

    unread_notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()

    return render(request, 'dashboard.html', {
        'posts': posts,
        'top_creators': top_creators,
        'trending_posts': trending_posts,
        'new_members': new_members,
        'unread_notifications': unread_notifications,
    })

def profile_page(request, username=None):

    # 1. Decide whose profile we're viewing
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user

    # 2. Posts for that profile
    user_posts = Post.objects.filter(
        user=profile_user
    ).order_by("-created_at")

    # 3. Saved posts ONLY for owner
    saved_posts = Post.objects.filter(
        bookmark__user=profile_user
    ).distinct().order_by("-created_at") if request.user == profile_user else None

    # 4. Follow system data
    followers_count = Follow.objects.filter(
        following=profile_user
    ).count()

    following_count = Follow.objects.filter(
        follower=profile_user
    ).count()

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()


    likes_received = sum(post.likes.count() for post in user_posts)

    posts_count = user_posts.count()

    followers_count = Follow.objects.filter(
        following=profile_user
    ).count()

    comments_received = Comment.objects.filter(
        post__user=profile_user
    ).count()

    saved_count = Bookmark.objects.filter(
    post__user=profile_user
).count()

    glow_score = (
        (posts_count * 10)
        + (likes_received * 2)
        + (comments_received * 3)
        + (followers_count * 10)
        + (saved_count * 5)
    )

    context = {
        "profile_user": profile_user,
        "user_posts": user_posts,
        "saved_posts": saved_posts,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "glow_score": glow_score,
    }

    return render(request, "profile.html", context)



def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.user:
        return JsonResponse({"success": False, "error": "Not allowed"}, status=403)

    post.delete()
    return JsonResponse({"success": True, "post_id": post_id})


def discover(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user


    post_type = request.GET.get("type", "all")

    posts = Post.objects.all()

    if post_type != "all":
        posts = posts.filter(post_type=post_type)

    posts_count = posts.count()
    creators = User.objects.exclude(id=request.user.id)

    followers_count = Follow.objects.filter(
        following=profile_user
    ).count()

    following_count = Follow.objects.filter(
        follower=profile_user
    ).count()

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()

    followers_count = Follow.objects.filter(
        following=profile_user
    ).count()

    

    return render(request, "discover.html", {
        "posts": posts,
        "active_type": post_type,
        "creators": creators,
        "profile_user": profile_user,
        "posts_count": posts_count,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
    })


def discover_search(request):
    q = request.GET.get("q", "")

    posts = Post.objects.filter(
        Q(caption__icontains=q) |
        Q(post_type__icontains=q) |
        Q(user__username__icontains=q)
    ).order_by("-created_at")

    html = render_to_string(
        "partials/posts.html",
        {"posts": posts},
        request=request
    )

    return JsonResponse({
        "html": html,
        "count": posts.count()
    })

def explore(request):

    return render(request, "explore.html")

def community(request):
    return render(request, "community.html")




def get_chat(request, user_id):
    try:
        other_user = User.objects.get(id=user_id)

        conversation = Conversation.objects.filter(
            users=request.user
        ).filter(
            users=other_user
        ).first()

        if not conversation:
            conversation = Conversation.objects.create()
            conversation.users.add(request.user, other_user)

        messages = Message.objects.filter(
            conversation=conversation
        ).order_by("created_at")

        Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(
            sender=request.user
        ).update(is_read=True)

        return JsonResponse({
            "user": {
                "id": other_user.id,
                "username": other_user.username,
                "avatar": (
                    other_user.profile.profile_picture.url
                    if hasattr(other_user, "profile") and other_user.profile.profile_picture
                    else ""
                )
            },
            "messages": [
                {
                    "text": m.text,
                    "sender": m.sender_id,
                    "time": m.created_at.strftime("%I:%M %p"),
                    "is_me": m.sender_id == request.user.id
                }
                for m in messages
            ],
            "conversation_id": conversation.id,
        })

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    except Exception as e:
        print("CHAT API ERROR:", e)  # 🔥 THIS WILL SHOW REAL ISSUE
        return JsonResponse({"error": str(e)}, status=500)



from django.contrib.auth import get_user_model

User = get_user_model()

from django.utils import timezone

def message_page(request):

    users = User.objects.exclude(id=request.user.id)

    user_list = []
    filter_type = request.GET.get("filter", "all")

    for u in users:

        conversation = Conversation.objects.filter(
            users=request.user
        ).filter(
            users=u
        ).first()

        unread = 0
        last_time = None

        if conversation:

            last_msg = Message.objects.filter(
                conversation=conversation
            ).order_by("-created_at").first()

            if last_msg:
                last_time = last_msg.created_at

            unread = Message.objects.filter(
                conversation=conversation,
                is_read=False
            ).exclude(sender=request.user).count()

            u.conversation_id = conversation.id

        u.unread_count = unread

        # fallback: ensure sorting never breaks
        u.last_message_time = last_time or (
            conversation.created_at if conversation else u.date_joined
        )

        user_list.append(u)

    # 🔥 SORT ONCE (IMPORTANT)
    user_list.sort(
        key=lambda x: x.last_message_time,
        reverse=True
    )

    # 🔥 FILTER AFTER SORTING
    if filter_type == "unread":
        user_list = [u for u in user_list if u.unread_count > 0]

    users = user_list

    selected_user_id = request.GET.get("user")

    conversation = None
    messages = []
    other_user = None

    if selected_user_id:
        other_user = User.objects.get(id=selected_user_id)

        conversations = Conversation.objects.filter(
            users=request.user
        ).filter(
            users=other_user
        )

        if conversations.exists():
            conversation = conversations.first()
        else:
            conversation = Conversation.objects.create()
            conversation.users.add(request.user, other_user)

        messages = Message.objects.filter(
            conversation=conversation
        ).order_by("created_at")

    unread_count = Message.objects.filter(
        conversation__users=request.user,
        is_read=False
    ).exclude(sender=request.user).count()

    return render(request, "messages.html", {
        "users": users,
        "messages": messages,
        "other_user": other_user,
        "conversation": conversation,
        "unread_count": unread_count,
        "active_filter": filter_type,
    })
@login_required
def settings(request):
    if request.method == "POST":
        user = request.user

        username = request.POST.get("username")
        email = request.POST.get("email")
        full_name = request.POST.get("full_name")
        bio = request.POST.get("bio")

        if username:
            user.username = username

        if email:
            user.email = email

        if full_name:
            parts = full_name.split(" ", 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ""

        user.save()

        # 🔥 FIX HERE (auto-create profile if missing)
        profile, created = Profile.objects.get_or_create(user=user)

        profile.bio = bio

        if request.FILES.get("profilePhoto"):
            profile.profile_picture = request.FILES["profilePhoto"]

        profile.save()

    return render(request, "settings.html")

from django.db.models import Count

def boards(request):
    boards_qs = Post.objects.exclude(
        post_type__isnull=True
    ).exclude(
        post_type=""
    ).exclude(
        image=""
    ).exclude(
        image__isnull=True
    )

    boards_data = boards_qs.values('post_type').annotate(
        post_count=Count('id')
    )

    boards = []

    for b in boards_data:
        posts = Post.objects.filter(
            post_type=b['post_type']
        ).exclude(
            image=""
        ).exclude(
            image__isnull=True
        )

        boards.append({
            "name": b['post_type'],
            "count": posts.count(),
            "posts": posts[:3],
        })

    return render(request, "boards.html", {"boards": boards})

def createpost2(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            print("POST SAVED:", post)  # DEBUG
            return redirect('dashboard')

        else:
            print("FORM ERRORS:", form.errors)  # IMPORTANT

    else:
        form = PostForm()

    return render(request, 'createpost2.html', {'form': form})


# def createpost2(request):
#     if request.method == "POST":
#         caption = request.POST.get("caption")
#         image = request.FILES.get("image")

#         if caption and image:
#             Post.objects.create(
#                 user=request.user,
#                 caption=caption,
#                 image=image
#             )

#             return redirect("dashboard")

#     return render(request, "createpost2.html")

