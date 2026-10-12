from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path("login/", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path('logout/', views.logout_view, name='logout'),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile_page, name="profile"),
    path("profile/<str:username>/", views.profile_page, name="creator_profile"),
    path("explore/", views.explore, name="explore"),
    path("community/", views.community, name="community"),

    path("messages/", views.message_page, name="messages"),
    path("settings/", views.settings, name="settings"),
    path("discover/", views.discover, name="discover"),
    path("boards/", views.boards, name="boards"),
    path("createpost2/", views.createpost2, name="createpost2"),

    path("update-profile-picture/", views.update_profile_picture, name="update_profile_picture"),

    path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('bookmark/<int:post_id>/', views.bookmark_post, name='bookmark_post'),

    path("comment/delete/<int:comment_id>/", views.delete_comment, name="delete_comment"),

    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),

    path("follow/<str:username>/", views.toggle_follow, name="toggle_follow"),

    path( "ajax/following-feed/",views.following_feed, name="following_feed"),

    path( "load-feed/",views.load_feed,name="load_feed"),

    path("api/chat/<int:user_id>/", views.get_chat, name="get_chat"),

    path("api/search-users/", views.search_users),

    path("api/dashboard-search/", views.dashboard_search),

    path( "api/discover-search/",  views.discover_search, name="discover_search"),
    path("notifications/", views.get_notifications, name="get_notifications"),

    path("notifications/read/",views.mark_notifications_read,name="mark_notifications_read"),

    # path("api/post/<int:post_id>/", views.get_post, name="get_post"),
   
]