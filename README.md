# CPSC450 - Bioinformatics

This project was designed to provide researchers with a simpler way to access the KEGG database. 
Users can request pathways that, with an accompanying dataset, will be displayed in a multitude of different ways such as 
tables and heatmaps.

This project requires the users to install some python packages.  To install everything needed for this project to run:

    pip3 install plotly dash bioservices pandas dash-html-components dash-core-components dash-table-experiments
    
Once you have all those installed you can run the app by running:

    python3 app.py
    
You'll see a bunch of stuff pop up in the commandline.  After that, navigate to:

    localhost:8050
    
from here you'll be able to use the entire app.  Everything is contained on one page.
