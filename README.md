# SyllabiShare

SyllabiShare is a web application created at the University of Virginia after seeing that a lot of our students wanted to see a class's syllabus and policies before signing up for it, and there was no streamlined way to do this. Our app allows students to share the syllabi of their classes with all the other students using the app at their school. This makes the process of choosing which classes to take easier, all while giving the students the peace of mind that they will be able to have a head start on the classes they chose.

## Getting Started

These instructions will detail how to use SyllabiShare.

### URL: http://syllabi-share.herokuapp.com/

### Logging In and Logging Out

We use Google OAuth to handle logging into our application, so as long as you have a university-related .edu Google Account you can use it. Simply click the button that says "Please Login with a .edu Email" and it will take you to the Google login screen. To logout click your username at the top right corner. It opens a dropdown menu, then click the "Logout" button to logout. Login is to help identify which school you come from so that we can direct you to the correct syllabi. 

### Uploading a Syllabus

To upload a syllabus click the bottom left corner of the home page or by clicking the upload button on the found on the upper right of the webpage. Please fill in the professor's name and course of the syllabus you intend to upload. Then select the syllabus from your computer and upload it. The syllabus must be smaller than 1 MB and must be a PDF for security reasons, otherwise it will not allow you to upload. Once you have done this, click submit to finish the upload process. You should see a green 'Addition Successful' confirmation pop up. It is important to note that until SyllabiShare has a professor consent system developed it is up to the uploader to ensure that they are not violating any policies of their university by uploading a syllabus. 

### Finding a Syllabus

SyllabiShare sorts syllabi by department so you can find a specific syllabus at the page that corresponds to its department. We also allow you to search for syllabi by the course identifiers (CS 2150) or the professor. We intend to add course names to our uploads soon&trade; and those will be searchable as well. SyllabiShare is reliant on students uploading syllabi so it is possible that you do not find a syllabus that you are looking for due to it not being uploaded yet. We will add a feature to request syllabi directly from professors soon&trade;.

### Leaderboard

The Leaderboard shows the top uploaders of SyllabiShare for each school. We are currently working on an opt-out feature soon&trade; so those who do not want to see their username displayed will not have to refrain from uploading. 

### Feedback

The developers of SyllabiShare do not pretend to be perfect and recognize that feedback is an important part of the development process. Therefore if you have found a bug or have a suggestion for us to implement in the app we highly recommend you leave feedback by clicking the feedback link on the upper right tab. We ask that you open a Github issue as well and connect it to your feedback in order for us to keep track of it at one easy location.

### Delete your Account

To delete your account click your email at the top right corner of any page. It will open a drop-down menu where you can click Settings. There it will ask you if you want to delete your account and to confirm the deletion of your account by typing your username. Once you have deleted your account you will be redirected to the login screen, which confirms your account was deleted. However, we must keep record of what you have uploaded and when you uploaded it.

### Technical Details

This app was written in Python using the Django Framework and is hosted on Heroku, with files being served through an Amazon Web Services S3 Bucket in Northern Virginia. This will eventually cost money, which is why I will once again ask for your financial support and ask that you click the Donate link at the bottom  of the screen and donate if you are able to. We understand if you can't though, we're all college students here.

## Authors

* **Vernon Andrade** - *Development, Lead*
* **Robbie B** - *Development*
* **Peter B** - *Documentation*
* **Winston Liu** - *Development, UI/UX*
