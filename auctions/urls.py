from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.createListing, name="create"),
    path("listing/<str:listing_name>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("addComment/<int:listing_id>", views.addComment, name="addComment"),
    path("addBid/<int:listing_id>", views.addBid, name="addBid"),
    path("closeAuction/<str:listing_name>", views.closeAuction, name="closeAuction"),
]
