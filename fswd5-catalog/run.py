from app import app

if __name__ == '__main__':
    
    # Run app locally only
    app.run(debug=True, port=1121)

    # Run app on externally visible server.
    # This means that server can be accessed by anyone on local network
    # by going to host's IP address in browser
    #
    # app.run(debug=True, host='0.0.0.0'
