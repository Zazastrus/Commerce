from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listings, Category, Comment, Bid


def index(request):
    if request.method == "POST":
        categ = request.POST["category"]
        category = Category.objects.get(categoryName=categ)
        return render(request, "auctions/index.html", {
            "listings": Listings.objects.filter(category=category).all(),
            "categories": Category.objects.all(),
        })

    active_listings = Listings.objects.filter(isActive=True).all()
    return render(request, "auctions/index.html", 
                  {"listings": active_listings,
                   "categories": Category.objects.all()})


def createListing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        imageUrl = request.POST["imageUrl"]
        price = float(request.POST["price"])
        category = Category.objects.get(categoryName=request.POST["category"])
        user = request.user
        bid = Bid(bid=price, user=user)
        bid.save()
        newListing = Listings(
            title=title,
            description=description,
            imageUrl=imageUrl,
            price=bid,
            category=category,
            owner=user
        )
        newListing.save()
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create.html", {"categories": Category.objects.all()})


def listing(request, listing_name):
    if request.method == "POST":
        listingId = request.POST["listing_id"]
        todo = request.POST["todo"]
        listing = Listings.objects.get(pk=listingId)
        isOwner = request.user.username == listing.owner.username
        if todo == "add":
            listing.watchlist.add(request.user)
            inWatchlist = request.user in listing.watchlist.all()
            comments = Comment.objects.filter(listing=listing)
            return render(request, "auctions/listing.html", {"listing": listing,
                                                            "price": f"{listing.price.bid:.2f}",
                                                            "inWatchlist": inWatchlist,
                                                            "comments": comments,
                                                            "isOwner":isOwner,
                                                            "isActive":listing.isActive})
        elif todo == "remove":
            listing.watchlist.remove(request.user)
            inWatchlist = request.user in listing.watchlist.all()
            comments = Comment.objects.filter(listing=listing)
            return render(request, "auctions/listing.html", {"listing": listing,
                                                            "price": f"{listing.price.bid:.2f}",
                                                            "inWatchlist": inWatchlist,
                                                            "comments": comments,
                                                            "isOwner":isOwner,
                                                            "isActive":listing.isActive})

    listing = Listings.objects.get(title=listing_name)
    inWatchlist = request.user in listing.watchlist.all()
    comments = Comment.objects.filter(listing=listing)
    isOwner = request.user.username == listing.owner.username
    return render(request, "auctions/listing.html", {"listing": listing,
                                                     "price": f"{listing.price.bid:.2f}",
                                                     "inWatchlist": inWatchlist,
                                                     "comments": comments,
                                                     "isOwner":isOwner,
                                                     "isActive":listing.isActive})

def closeAuction(request, listing_name):
    id = request.POST["listing_id"]
    listing = Listings.objects.get(pk=id)
    listing.isActive = False
    listing.save()
    comments = Comment.objects.filter(listing=listing)
    inWatchlist = request.user in listing.watchlist.all()
    return render(request, "auctions/listing.html", {"listing": listing,
                                                         "price": f"{listing.price.bid:.2f}",
                                                         "inWatchlist": inWatchlist,
                                                         "comments":comments,
                                                         "message": "Your auction is closed!",
                                                         "updated": True,
                                                         "isActive":listing.isActive
                                                         })


def addBid(request, listing_id):
    listing = Listings.objects.get(pk=listing_id)
    oldBid = listing.price.bid
    inWatchlist = request.user in listing.watchlist.all()
    comments = Comment.objects.filter(listing=listing)
    newBid = (request.POST["bid"])
    if not newBid or float(newBid) == oldBid:
        return render(request, "auctions/listing.html", {"listing": listing,
                                                         "price": f"{listing.price.bid:.2f}",
                                                         "inWatchlist": inWatchlist,
                                                         "comments":comments,
                                                         "message": "Bid updated failed",
                                                         "updated": False,
                                                         "isActive":listing.isActive
                                                         })
    elif float(newBid) > oldBid:
        updateBid = Bid(bid=float(newBid), user=request.user)
        updateBid.save()
        listing.price = updateBid
        listing.save()
        # *args and **kwargs can't be passed to reverse() at the same time
        #return HttpResponseRedirect(reverse("listing", args=[listing.title], kwargs={"message":"Bid updated successfully", "updated":True}))
        return render(request, "auctions/listing.html", {"listing": listing,
                                                         "price": f"{listing.price.bid:.2f}",
                                                         "inWatchlist": inWatchlist,
                                                         "comments":comments,
                                                         "message": "Bid updated successfully",
                                                         "updated": True,
                                                         "isActive":listing.isActive
    
                                                     })
    #return HttpResponseRedirect(reverse("listing", args=[listing.title]))

def watchlist(request):
    listings = Listings.objects.filter(watchlist=request.user)
    return render(request, "auctions/watchlist.html", {"listings": listings})

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {"categories": categories})

def addComment(request, listing_id):
    if request.method == "POST":
        comment = request.POST["comment"]
        listing = Listings.objects.get(pk=listing_id)
        newComment = Comment(author=request.user, listing=listing, comment=comment)
        newComment.save()
        return HttpResponseRedirect(reverse("listing", args=[listing.title]))

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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    