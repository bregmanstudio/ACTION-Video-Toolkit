ACTION
======

Public repo for the ACTION project at Dartmouth

Check out http://bregman.dartmouth.edu/action for more information!

Welcome to the ACTION toolbox from the Bregman Music and Audio Research Studio at Dartmouth College. These pages document the toolbox and show examples of its use.

What is ACTION?
---------------

Audio-visual Cinematic Toolkit for Interaction, Organization, and Navigation

ACTION provides a work bench to study such features in combination with machine learning methods to yield latent stylistic patterns distributed among films and directors. As such, ACTION is a platform for researching new methodologies in the study of film and media history.

The platform allows such features as access to and analysis of low-level frame-by-frame data, automated segmentation and clustering of this data, audio analysis for soundtracks, and other content analysis tools. ACTION provides Python tools to support research and development, and depends on the Bregman Python Toolkit. OpenCV 2.4 compiled with Python bindings is required for analysis.

Co-principle investigators: Michael Casey (Bregman) and Mark Williams (Film and Media Studies). Postdoctoral researcher: Tom Stoll (Bregman). Sponsored by the National Endowment for the Humanities (NEH), Office of Digital Humanities (ODH) Grant #HD-51394-11

Who Is ACTION for?
------------------

ACTION provides Python tools to support research and development including, but not limited to:
- Multimedia IR - explore methods for video information retrieval (requires OpenCV package)
- See Bregman’s documentation index for a similar list of aims.

How is ACTION Used?
-------------------

Using ACTION is as easy as:

```
from action import *
cfl = ColorFeaturesLAB('North_by_Northwest')
cfl.analyze_movie()
```

...then access the analysis data:

```
myseg = Segment(0, cfl.determine_movie_length())
data = cfl.full_color_features_for_segment(myseg)
```

You can also view the data alongside the imagery of the film:

```
cfl.playback_movie()
```

ACTION also has functionality for analyzing and accessing optical flow (movement) information and audio analysis metadata.

More Information
----------------
Check out http://bregman.dartmouth.edu/action for more information!
