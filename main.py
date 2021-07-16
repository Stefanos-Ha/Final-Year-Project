from collections import defaultdict
import re


def loadRatings():

    print("Loading rating.csv...")

    # initialize the dictionary
    ratings = defaultdict(dict)

    with open("rating.csv", encoding="utf-8") as fp:

        # skip the header row
        next(fp, None)

        for line in fp.readlines():

            # split at commas and convert to integers
            line = line.strip().split(",")
            user_id, anime_id, rating = [int(i) for i in line]

            # add the entry to the dictionary
            ratings[user_id][anime_id] = rating

    return ratings


def loadAnime():

    print("Loading anime.csv...")

    animes = {}
    name2id = {}

    with open("anime.csv", encoding="utf-8") as fp:
        next(fp, None)

        for line in fp.readlines():
            # strip the line from terminal spaces
            line = line.strip()

            # remove commas inside quotes
            line = re.sub(r'(?!(([^"]*"){2})*[^"]*$),', '', line)

            # split at commas
            anime_id, name, genres, typ, episodes, rating, members = line.split(",")

            # default type in TV
            # 'ONA', 'TV', 'Movie', 'Music', 'OVA', 'Special'
            if typ == "":
                typ = "TV"

            # type conversion
            anime_id = int(anime_id)
            members = int(members)

            # add the entry to the dictionary
            animes[anime_id] = {"name": name, "genres": genres,
                                "type": typ, "episodes": episodes,
                                "rating": rating, "members": members}

            name2id[name] = anime_id

    return animes, name2id


def most_similar(userVector, ratings, k=20):
    """
    returns a list of k most similar users to the userVector
    using collaborative filtering
    """

    user_keys = set(userVector.keys())
    rank = []

    print("\nComputing similarity scores...")

    # go through every single user
    for user, vector in ratings.items():

        # the set of common anime they watched
        common_keys = user_keys.intersection(set(vector.keys()))

        # if no common shows are present, continue
        if len(common_keys) == 0:
            continue

        # compute the distance and add the entry to the list 
        dist = sum((userVector[key] - vector[key]) ** 2 for key in common_keys)
        rank.append((user, dist))

    # sort the list by distance and return the k closest users
    rank.sort(key=lambda x: x[1])
    return rank[:k]


def recommand(userVector, ratings, animes, genres, types, k=5):
    """
    returns a list of k recommended shows
    """

    # identify the shows to recommend
    rank = most_similar(userVector, ratings)

    shows = defaultdict(int)

    # go through each similar user
    for user, _ in rank:

        for show in ratings[user].keys():
            if show not in userVector.keys():

                # filter by the genres
                if any(g in animes[show]["genres"] for g in genres):

                    # filter by the type
                    if animes[show]["type"] in types:

                        # use the popularity of the show as points
                        anime = animes[show]["name"]
                        popularity = animes[show]["members"]
                        shows[anime] += popularity

    # sort the shows by highest scores (popularity * number of times it was recommend)
    recs = sorted(shows.items(), key=lambda x: x[1], reverse=True)

    # removing the scores
    recs = [show for show, score in recs]

    # number of items to recommend
    k = min(k, len(recs))

    # return the k best recommendations
    return recs[:k]


if __name__ == "__main__":

    # load the data
    ratings = loadRatings()
    animes, name2id = loadAnime()

    # infinite loop
    while True:

        userVector = {}
        print("\nEnter your vector then press Return search for recommendations:")

        while True:
            # ask the user for the entries
            entry = input("Enter an (anime_name -- rating) pair: ")

            if not entry.strip():
                break

            # add the entry to the vector
            try:
                anime_name, rating = entry.strip().split(" -- ")

                anime_id = name2id[anime_name]
                rating = int(rating)
            except:
                print("Please enter a valid rating.")
                continue

            userVector[anime_id] = rating

        # if the vector is empty, continue
        if len(userVector) == 0:
            print("Please enter at least one rating for a show.")

        else:

            print("\nSelect genres to filter by. To select all genres, you")
            print("can either type ALL, or Press Return as your first entry\n")

            genres = []

            while True:
                genre = input("Enter a genre: ").strip().capitalize()

                if genre == "ALL":
                    genre = ""

                if genre == "":
                    break

                genres.append(genre)

            # if no genres are entered, don't filter
            if len(genres) == 0:
                genres = [""]

            # select types
            print("\nSelect types to filter by.")
            print("Enter the types you wish, separated by a space.")

            print("Types: ONA, TV, Movie, OVA, Special")

            types = input("\nEnter types: ").strip().split()

            # compute the recommendations
            recs = recommand(userVector, ratings, animes, genres, types)

            # print the recommendations
            print("\nWe recommend you watch:")
            for n, show in enumerate(recs):
                print(f"{n+1}- {show}")

        # exit message
        ans = input("Do you want to enter another vector? [y/n] ")

        if ans.lower() == "n":
            break
