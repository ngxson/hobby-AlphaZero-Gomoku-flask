# For development use (simple logging, etc):
python server.py
# For production use: 
# gunicorn server:app -w 10 --log-file -