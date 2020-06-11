# SyllabiShare

### Link: http://syllabi-share.herokuapp.com/

SyllabiShare is a web application created at the University of Virginia after seeing the unmet need of a lot of our students wanting to see a class's syllabus and policies before registering for it.

SyllabiShare allows students to share the syllabi of classes with all the other students using the app at their school. This app streamlines the process of choosing which classes to take and be informed along the way.


## Usage

### Logging In and Logging Out

SyllabiShare requires a university-provided .edu Google Account to use it. 

Simply click the button that says "Please Login with a .edu Email" and it will take you to the Google login screen. 

To logout, click your username at the top right corner. 

### Uploading a Syllabus

To upload a syllabus:
- Click the bottom left corner of the home page or by clicking the upload button on the found on the upper right of the webpage. 
- Fill in the professor's name and course of the syllabus. 
- Then select the syllabus from your computer and upload it. (Required: PDF, <1 MB size) 
- Click submit to finish.
- You should see a green 'Addition Successful' confirmation pop up. 

_Note: it is up to the uploader to ensure that the users are not violating any policies of their university by uploading a syllabus._ 

### Finding a Syllabus

SyllabiShare sorts syllabi by department so you can find a specific syllabus at the page that corresponds to its department. 

You can also search for syllabi by the course identifiers (CS 2150) or the professor. 

_Note: You might not find a syllabus you desire since SyllabiShare relies on students uploading the syllabi._


### Leaderboard

The Leaderboard shows the top uploaders of SyllabiShare for each school. 
Currently, this is opt-in by default.

### Delete your Account

- To delete your account click your email at the top right corner of any page. 
- It will open a drop-down menu where you can click Settings. There it will ask you if you want to delete your account and to confirm the deletion of your account by typing your username. 
- Once you have deleted your account you will be redirected to the login screen, which confirms your account was deleted. 

_Note: However, we must keep record of what you have uploaded and when you uploaded it._

### Feedback

The developers of SyllabiShare do not pretend to be perfect and recognize that feedback is an important part of the development process. Therefore if you have found a bug or have a suggestion for us to implement in the app we highly recommend you leave feedback by clicking the feedback link on the upper right tab. We ask that you open a Github issue as well and connect it to your feedback in order for us to keep track of it at one easy location.

### Roadmap:

[ ] Add feature to include course names for syllabus uploads and be searchable

[ ] Add a feature to request syllabi directly from professors

[ ] Implement opt-out leaderboard to give option to users not to display username

----

### Technical Details

- Language & Framework: **Python, Django**
- Webapp Hosting:  **Heroku**, 
- Files Storage: **AWS S3** Bucket (Northern Virginia)
- User Authenication: **Google OAuth**

These service providers will eventually cost money, which is why we humbly ask for your financial support. 
Please support us by clicking `Donate link` at the bottom of the screen if you are able to. 

## Authors

* **Vernon Andrade** - *Development, Lead*
* **Robbie B** - *Development*
* **Peter B** - *Documentation*
* **Winston Liu** - *Development, UI/UX*
