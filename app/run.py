from app import create_app
from app.data import main
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
    # main()
