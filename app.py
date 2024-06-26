from flask import Flask, render_template, request
import instaloader

app = Flask(__name__)

def login(username, password):
    try:
        L = instaloader.Instaloader()
        L.context.log("Logging in...")
        L.login(username, password)
        L.context.log("Login successful!")
        return L
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        two_factor_code = input("Enter the two-factor authentication code: ")
        L.context.two_factor_code = two_factor_code
        L.context.log("Two-factor authentication code entered")
        L.context.log("Logging in...")
        L.login(username, password)
        L.context.log("Login successful!")
        return L
    except instaloader.exceptions.InvalidArgumentException as e:
        print("Login failed:", e)
    except instaloader.exceptions.BadCredentialsException as e:
        print("Login failed: Incorrect password.")
    except Exception as e:
        print("An unexpected error occurred during login:", e)
    return None

def get_followers_and_following(L, username):
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        followers = profile.get_followers()
        following = profile.get_followees()

        followers_list = [{"username": follower.username, "url": f"https://www.instagram.com/{follower.username}/"} for follower in followers]
        following_list = [{"username": user.username, "url": f"https://www.instagram.com/{user.username}/"} for user in following]

        unfollowers = [user for user in following_list if user not in followers_list]
        not_following_back = [user for user in followers_list if user not in following_list]

        return {
            "followers_list": followers_list,
            "following_list": following_list,
            "unfollowers": unfollowers,
            "not_following_back": not_following_back,
        }

    except Exception as e:
        print("An unexpected error occurred while getting followers:", e)
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        L = login(username, password)
        if L:
            data = get_followers_and_following(L, username)
            return render_template('index.html', data=data)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
