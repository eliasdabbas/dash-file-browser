

# Dash File Browser

A simple file browser for Plotly Dash applications.

- Allow users to interactively browse files and folders on the server
- Show folder icons for differentiation
- Expose files and folder as objects to be manipulated by your Dash app

![](dash_file_browser.gif)


To run: 

```bash
pip install -r requirements

python app.py

# OR with gunicorn (needs to also be installed):

gunicorn app:server
```