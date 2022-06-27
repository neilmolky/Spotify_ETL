from urllib.parse import quote
import requests

# enter your personal spotify user ID
user_id = ""  # Keep once finished

# enter the client ID and secret for the app you made in the spotify dashboard that will access your user information
recent_songs_id = ""  # Keep once finished
recent_songs_secret = ""  # Keep once finished

# enter the redirect uri you have given permission for this app to use
redirect_uri = ""

# enter the client ID and secret for the app you made in the spotify dashboard that will access track features
track_features_id = ""  # Keep once finished
track_features_secret = ""  # Keep once finished

# follow the instructions in this file to populate the following fields
authorization_code = ""
recent_songs_token = ""  # Keep once finished

# examine the functions below or scroll to the bottom to get started
def show_url_for_redirect():
    """
    this function will produce a url and print it.
    paste this into your browser to grant authorisation for the program
    :return:
    """
    url_parameters = {
        "client_id": recent_songs_id,
        "response_type": "code",
        "redirect_uri": quote(redirect_uri),
        "scope": "user-read-recently-played"

    }
    url = "https://accounts.spotify.com/authorize?" + "&".join(
        [key + "=" + value for key, value in url_parameters.items()]
    )
    print(url)

def extract_code(redirected_url):
    parts = redirected_url.split("?")
    code = parts[-1]
    if code.startswith("code="):
        parts = code.split("&")
        if type(code) == "list":
            code = code[0]
        print(code[5:])
    else:
        print("code not found!")

def first_contact():
    """
    first contact with the spotify OAuth protocol
    you will need to create your app in spotify's dashboard to get the recent_songs_id and recent_songs_secret
    import them into your secrets file
    :return:
    """
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": redirect_uri,
        "recent_songs_id": recent_songs_id,
        "recent_songs_secret": recent_songs_secret,
    }
    r = requests.post(url, data=data)

    print(r.json())

    if r:
        response = r.json()
        print(response)
        api_token = response["access_token"]
        print("testing connection")
        if test_connection(api_token):
            print("check your data and if it looks right record your refresh token in this secret file")
            print("your refresh token is:", response["recent_songs_token"])
        else:
            print("something went wrong when using your API token. "
                  "Please regenerate a client authorization code and try again")


def test_connection(token):
    url = "https://api.spotify.com/v1/me/player/recently-played"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    r = requests.get(url, headers=headers)
    print(r)
    data = r.json()
    print(data["items"])
    return bool(r)



if __name__ == "__main__":
    """
    before you begin copy this file and rename it to secrets. make sure this file is secure!
    
    make_secrets is designed to help you build this part of the program, the rest of the package uses the spotify_recently_played secrets
    if you do not create a file named secrets with the correct information in you will encounter errors
    
    feel free to run the below commented out lines of code in order and follow the instructions.
    you can delete the lines of code as you go in order to populate your secrets file
    when you've populated your secrets file delete the redundant code.
    
    for example, in this first function we print out on screen the authorization code your app will require
    when making requests to the spotify server.
    run the function below and copy and paste the output into the client_authorization attribute 
    declared at the top of the file. 
    """
    # show_client_authorisation()
    """
    When you run the next function it will print a link, follow this to be redirected to the authorization uri
    You will be asked if you give permission for your application to access your spotify data
    if you allow you will be redirected to the redirect uri you provided.
    if you look at the address bar in the browser you can see additional text has been stored at the end of the url
    eg www.redirect.com$code=hsapfboiw$scope=
    you are interested in the "code=" part of the url. 
    either extract it yourself or use the extract_code function to extract the code by passing it the full url
    of the redirected webpage
    """
    # show_url_for_redirect()
    # extract_code("")
    """
    Finally we can create our tokens and test to see if it returns what we want.
    If it returns a JSON file it will look like a dictionary and you should be able to see your recently playyed songs. 
    If something goes wrong, try again with a new Auth code and re-read the instructions and/or flag this for review.
    """
    # first_contact()
    """
    remember to save your username, client_authentication and refresh token
    all other code in this file can now be deleted as long as you have renamed it spotify_secrets.py
    """
