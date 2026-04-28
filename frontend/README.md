# rent-equipment_website
example website where you can rent machinery.


how to launch:

make your venv in /backend directory with command
  python -m venv .venv
(works only if you using linux)

Then activate your venv:
  source .venv/bin/activate

Then install all requirements:
  pip install -r requirements.txt
  
Then launch backend from /backend directory with command:
  uvicorn main:app --reload

Then launch frontend on localhost from /frontend directory:
  python -m localhost.server 5500

And finally go to the address below in your browser:
  http://localhost:5500
